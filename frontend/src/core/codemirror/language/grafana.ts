/* Copyright 2024 Marimo. All rights reserved. */
import { LanguageAdapter, LanguageAdapterType } from "./types";
import { CompletionConfig } from "@/core/config/config-schema";
import { HotkeyProvider } from "@/core/hotkeys/hotkeys";
import { Extension } from "@codemirror/state";
import { PlaceholderType } from "../config/extension";
import { MovementCallbacks } from "../cells/extensions";
import { basicSetup } from "@codemirror/basic-setup";
import { json } from "@codemirror/lang-json";

/**
 * Grafana Language Adapter
 * 
 * This adapter provides syntax highlighting for Grafana dashboard embedding
 */
export class GrafanaLanguageAdapter implements LanguageAdapter {
  readonly type: LanguageAdapterType = "grafana";
  readonly defaultCode: string = "# Grafana Dashboard\n# url: http://localhost:3000\n# dashboardUID: your-dashboard-uid\n# from: now-6h\n# to: now\n# theme: light\n# height: 600px\n";

  transformIn(code: string): [string, number] {
    // No transformation needed, return the code as is
    return [code, 0];
  }

  transformOut(code: string): [string, number] {
    // No transformation needed, return the code as is
    return [code, 0];
  }

  isSupported(code: string): boolean {
    // Simple heuristic - check if there are Grafana dashboard metadata
    return (
      code.includes("# Grafana Dashboard") ||
      code.includes("# dashboardUID:") ||
      code.includes("dashboardUID:") ||
      code.includes("# panelId:") ||
      code.includes("panelId:")
    );
  }

  getExtension(
    completionConfig: CompletionConfig,
    hotkeys: HotkeyProvider,
    placeholderType: PlaceholderType,
    movementCallbacks: MovementCallbacks
  ): Extension[] {
    // Using JSON syntax highlighting as a base for the dashboard configuration
    return [
      basicSetup,
      json(),
    ];
  }
} 