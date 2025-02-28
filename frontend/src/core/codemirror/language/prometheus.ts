/* Copyright 2024 Marimo. All rights reserved. */
import { LanguageAdapter, LanguageAdapterType } from "./types";
import { CompletionConfig } from "@/core/config/config-schema";
import { HotkeyProvider } from "@/core/hotkeys/hotkeys";
import { Extension } from "@codemirror/state";
import { PlaceholderType } from "../config/extension";
import { MovementCallbacks } from "../cells/extensions";
import { basicSetup } from "@codemirror/basic-setup";
import { sql, SQLDialect } from "@codemirror/lang-sql";

/**
 * PromQL Language Adapter
 * 
 * This adapter provides syntax highlighting and autocompletion for PromQL queries
 */
export class PrometheusLanguageAdapter implements LanguageAdapter {
  readonly type: LanguageAdapterType = "prometheus";
  readonly defaultCode: string = "# Prometheus Query\n# url: http://localhost:9090\n\nrate(http_requests_total{job=\"api-server\"}[5m])";

  transformIn(code: string): [string, number] {
    // No transformation needed, return the code as is
    return [code, 0];
  }

  transformOut(code: string): [string, number] {
    // No transformation needed, return the code as is
    return [code, 0];
  }

  isSupported(code: string): boolean {
    // Simple heuristic - check if there are common PromQL functions or metrics
    return (
      code.includes("rate(") ||
      code.includes("sum(") ||
      code.includes("avg(") ||
      code.includes("count(") ||
      code.includes("max(") ||
      code.includes("min(") ||
      code.includes("_total") ||
      code.includes("_count") ||
      code.includes("_sum") ||
      code.includes("_bucket") ||
      /{[^}]*}/.test(code) || // Label selectors {job="..."}
      code.includes("# Prometheus Query")
    );
  }

  getExtension(
    completionConfig: CompletionConfig,
    hotkeys: HotkeyProvider,
    placeholderType: PlaceholderType,
    movementCallbacks: MovementCallbacks
  ): Extension[] {
    // Using SQL syntax highlighting as a base since it's somewhat similar
    const dialect = SQLDialect.define({});
    return [
      basicSetup,
      sql({ dialect }),
    ];
  }
} 