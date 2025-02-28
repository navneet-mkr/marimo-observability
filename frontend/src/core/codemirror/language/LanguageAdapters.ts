/* Copyright 2024 Marimo. All rights reserved. */
import type { LanguageAdapter, LanguageAdapterType } from "./types";
import { PythonLanguageAdapter } from "./python";
import { MarkdownLanguageAdapter } from "./markdown";
import { SQLLanguageAdapter } from "./sql";
import { PrometheusLanguageAdapter } from "./prometheus";
import { LokiLanguageAdapter } from "./loki";
import { GrafanaLanguageAdapter } from "./grafana";

export const LanguageAdapters: Record<
  LanguageAdapterType,
  () => LanguageAdapter
> = {
  python: () => new PythonLanguageAdapter(),
  markdown: () => new MarkdownLanguageAdapter(),
  sql: () => new SQLLanguageAdapter(),
  prometheus: () => new PrometheusLanguageAdapter(),
  loki: () => new LokiLanguageAdapter(),
  grafana: () => new GrafanaLanguageAdapter(),
};

export function getLanguageAdapters() {
  return Object.values(LanguageAdapters).map((la) => la());
}
