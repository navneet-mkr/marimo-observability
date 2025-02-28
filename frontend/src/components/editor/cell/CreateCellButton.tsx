/* Copyright 2024 Marimo. All rights reserved. */
import { DatabaseIcon, PlusIcon } from "lucide-react";
import { Button } from "@/components/editor/inputs/Inputs";
import { Tooltip } from "../../ui/tooltip";
import {
  ContextMenu,
  ContextMenuTrigger,
  ContextMenuContent,
  ContextMenuItem,
} from "@/components/ui/context-menu";
import { MarkdownLanguageAdapter } from "@/core/codemirror/language/markdown";
import { MarkdownIcon, PythonIcon, PrometheusIcon, LokiIcon, GrafanaIcon } from "./code/icons";
import { SQLLanguageAdapter } from "@/core/codemirror/language/sql";
import { PrometheusLanguageAdapter } from "@/core/codemirror/language/prometheus";
import { LokiLanguageAdapter } from "@/core/codemirror/language/loki";
import { GrafanaLanguageAdapter } from "@/core/codemirror/language/grafana";
import { cn } from "@/utils/cn";
import { Events } from "@/utils/events";

export const CreateCellButton = ({
  appClosed,
  onClick,
  tooltipContent,
}: {
  appClosed: boolean;
  tooltipContent: React.ReactNode;
  onClick: ((opts: { code: string }) => void) | undefined;
}) => {
  return (
    <CreateCellButtonContextMenu onClick={onClick}>
      <Tooltip content={tooltipContent} usePortal={false}>
        <Button
          onClick={() => onClick?.({ code: "" })}
          className={cn(
            "shoulder-button hover-action",
            appClosed && " inactive-button",
          )}
          onMouseDown={Events.preventFocus}
          shape="circle"
          size="small"
          color="hint-green"
          data-testid="create-cell-button"
        >
          <PlusIcon strokeWidth={1.8} />
        </Button>
      </Tooltip>
    </CreateCellButtonContextMenu>
  );
};

const CreateCellButtonContextMenu = (props: {
  onClick: ((opts: { code: string }) => void) | undefined;
  children: React.ReactNode;
}) => {
  const { children, onClick } = props;

  if (!onClick) {
    return children;
  }

  return (
    <ContextMenu>
      <ContextMenuTrigger>{children}</ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem
          key="python"
          onSelect={(evt) => {
            evt.stopPropagation();
            onClick({ code: "" });
          }}
        >
          <div className="mr-3 text-muted-foreground">
            <PythonIcon />
          </div>
          Python cell
        </ContextMenuItem>

        <ContextMenuItem
          key="markdown"
          onSelect={(evt) => {
            evt.stopPropagation();
            onClick({ code: new MarkdownLanguageAdapter().defaultCode });
          }}
        >
          <div className="mr-3 text-muted-foreground">
            <MarkdownIcon />
          </div>
          Markdown cell
        </ContextMenuItem>
        <ContextMenuItem
          key="sql"
          onSelect={(evt) => {
            evt.stopPropagation();
            onClick({ code: new SQLLanguageAdapter().getDefaultCode() });
          }}
        >
          <div className="mr-3 text-muted-foreground">
            <DatabaseIcon size={13} strokeWidth={1.5} />
          </div>
          SQL cell
        </ContextMenuItem>
        <ContextMenuItem
          key="prometheus"
          onSelect={(evt) => {
            evt.stopPropagation();
            onClick({ code: new PrometheusLanguageAdapter().defaultCode });
          }}
        >
          <div className="mr-3 text-muted-foreground">
            <PrometheusIcon />
          </div>
          Prometheus (PromQL) cell
        </ContextMenuItem>
        <ContextMenuItem
          key="loki"
          onSelect={(evt) => {
            evt.stopPropagation();
            onClick({ code: new LokiLanguageAdapter().defaultCode });
          }}
        >
          <div className="mr-3 text-muted-foreground">
            <LokiIcon />
          </div>
          Loki (LogQL) cell
        </ContextMenuItem>
        <ContextMenuItem
          key="grafana"
          onSelect={(evt) => {
            evt.stopPropagation();
            onClick({ code: new GrafanaLanguageAdapter().defaultCode });
          }}
        >
          <div className="mr-3 text-muted-foreground">
            <GrafanaIcon />
          </div>
          Grafana Dashboard cell
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
};
