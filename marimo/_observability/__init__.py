"""Observability module for Marimo.

This module provides specialized cell types and functions for interacting with
the Grafana observability stack (Prometheus, Loki, and Grafana dashboards).
"""

try:
    from marimo._observability.promql import promql
except ImportError as e:
    def promql(*args, **kwargs):
        raise ImportError(
            "Could not import promql. Please ensure you have installed the required dependencies: "
            "pandas, requests, pydantic. Error: " + str(e)
        )

try:
    from marimo._observability.logql import logql
except ImportError as e:
    def logql(*args, **kwargs):
        raise ImportError(
            "Could not import logql. Please ensure you have installed the required dependencies: "
            "pandas, requests, pydantic. Error: " + str(e)
        )

try:
    from marimo._observability.grafana import grafana_dashboard
except ImportError as e:
    def grafana_dashboard(*args, **kwargs):
        raise ImportError(
            "Could not import grafana_dashboard. Please ensure you have installed the required dependencies: "
            "requests. Error: " + str(e)
        )

__all__ = ["promql", "logql", "grafana_dashboard"]