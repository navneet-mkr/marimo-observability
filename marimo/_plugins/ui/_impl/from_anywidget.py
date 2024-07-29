# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

import json
import weakref
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

import marimo._output.data.data as mo_data
from marimo import _loggers
from marimo._output.rich_help import mddoc
from marimo._plugins.core.json_encoder import WebComponentEncoder
from marimo._plugins.ui._core.ui_element import UIElement
from marimo._runtime.functions import Function

if TYPE_CHECKING:
    from anywidget import (  # type: ignore [import-not-found,unused-ignore]  # noqa: E501
        AnyWidget,
    )

LOGGER = _loggers.marimo_logger()


# Weak dictionary
# When the widget is deleted, the UIElement will be deleted as well
cache: Dict[Any, UIElement[Any, Any]] = weakref.WeakKeyDictionary()  # type: ignore[no-untyped-call, unused-ignore, assignment]  # noqa: E501


def from_anywidget(widget: "AnyWidget") -> UIElement[Any, Any]:
    """Create a UIElement from an AnyWidget."""
    if widget not in cache:
        cache[widget] = anywidget(widget)  # type: ignore[no-untyped-call, unused-ignore, assignment]  # noqa: E501
    return cache[widget]


T = Dict[str, Any]


@dataclass
class SendToWidgetArgs:
    content: Any
    buffers: Optional[Any] = None


@mddoc
class anywidget(UIElement[T, T]):
    """
    Create a UIElement from an AnyWidget.
    This proxies all the widget's attributes and methods.

    **Example.**

    ```python
    from drawdata import ScatterWidget
    import marimo as mo

    scatter = ScatterWidget()
    scatter = mo.ui.anywidget(scatter)

    # In another cell, access its value
    # This works for all widgets
    scatter.value

    # Or attributes specifically on the ScatterWidget
    scatter.data_as_pandas
    scatter.data_as_polars
    ```

    **Attributes.**

    - `value`: The value of the widget's traits as a dictionary.
    - `widget`: The widget being wrapped.

    **Initialization Args.**

    - `widget`: The widget to wrap.
    """

    def __init__(self, widget: "AnyWidget"):
        self.widget = widget

        # Get all the traits of the widget
        args: T = widget.trait_values()
        ignored_traits = [
            "comm",
            "layout",
            "log",
            "tabbable",
            "tooltip",
            "keys",
            "_esm",
            "_anywidget_id",
            "_dom_classes",
            "_model_module",
            "_model_module_version",
            "_model_name",
            "_property_lock",
            "_states_to_send",
            "_view_count",
            "_view_module",
            "_view_module_version",
            "_view_name",
        ]
        # Remove ignored traits
        for trait_name in ignored_traits:
            args.pop(trait_name, None)
        # Keep only classes that are json serialize-able
        json_args: T = {}
        for k, v in args.items():
            try:
                # Try to see if it is json-serializable
                json.dumps(v, cls=WebComponentEncoder)
                # Just add the plain value, it will be json-serialized later
                json_args[k] = v
            except TypeError:
                pass

        def on_change(change: T) -> None:
            for key, value in change.items():
                widget.set_trait(key, value)

        js: str = widget._esm if hasattr(widget, "_esm") else ""  # type: ignore [unused-ignore]  # noqa: E501
        css: str = widget._css if hasattr(widget, "_css") else ""  # type: ignore [unused-ignore]  # noqa: E501

        self.widget.comm = _maybe_create_comm(self)

        super().__init__(
            component_name="marimo-anywidget",
            initial_value=json_args,
            label="",
            args={
                "js-url": mo_data.js(js).url if js else "",  # type: ignore [unused-ignore]  # noqa: E501
                "css": css,
            },
            on_change=on_change,
            functions=(
                Function(
                    name="send_to_widget",
                    arg_cls=SendToWidgetArgs,
                    function=self._receive_from_frontend,
                ),
            ),
        )

    def _send_to_frontend(
        self, value: T, buffers: Optional[Any] = None
    ) -> None:
        self.send_message(value, buffers)

    def _receive_from_frontend(self, args: SendToWidgetArgs) -> None:
        self.widget._handle_custom_msg(args.content, args.buffers)

    def _convert_value(self, value: T) -> T:
        return value

    # Proxy all the widget's attributes
    def __getattr__(self, name: str) -> Any:
        return getattr(self.widget, name)


def _maybe_create_comm(widget: "anywidget") -> Any:
    try:
        from comm.base_comm import BaseComm  # type: ignore

        class MarimoComm(BaseComm):  # type: ignore
            def publish_msg(
                self,
                msg_type: str,
                data: Any = None,
                metadata: Any = None,
                buffers: Any = None,
                **keys: Any,
            ) -> None:
                del metadata
                del keys
                if (
                    msg_type == "comm_msg"
                    and "method" in data
                    and data["method"] == "custom"
                ):
                    if "content" in data:
                        widget._send_to_frontend(data["content"], buffers)
                    else:
                        LOGGER.warning("No content in custom message")

        return MarimoComm()
    except ImportError:
        LOGGER.warning("Comm is not available")
