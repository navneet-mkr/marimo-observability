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
 * LogQL Language Adapter
 * 
 * This adapter provides syntax highlighting and autocompletion for LogQL queries
 */
export class LokiLanguageAdapter implements LanguageAdapter {
  readonly type: LanguageAdapterType = "loki";
  readonly defaultCode: string = "# Loki Query\n# url: http://localhost:3100\n\n{app=\"frontend\"} |= \"error\" | json";

  transformIn(code: string): [string, number] {
    // No transformation needed, return the code as is
    return [code, 0];
  }

  transformOut(code: string): [string, number] {
    // No transformation needed, return the code as is
    return [code, 0];
  }

  isSupported(code: string): boolean {
    // Simple heuristic - check if there are common LogQL patterns
    return (
      /\{[^}]*\}/.test(code) || // Log stream selector {app="frontend"}
      code.includes("|=") ||
      code.includes("!=") ||
      code.includes("|~") ||
      code.includes("!~") ||
      code.includes("| json") ||
      code.includes("| logfmt") ||
      code.includes("| pattern") ||
      code.includes("| regexp") ||
      code.includes("# Loki Query")
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