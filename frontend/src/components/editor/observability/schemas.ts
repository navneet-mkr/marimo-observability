/* Copyright 2024 Marimo. All rights reserved. */
import { z } from "zod";
import { FieldOptions } from "@/components/forms/options";

function passwordField() {
  return z
    .string()
    .optional()
    .describe(
      FieldOptions.of({
        label: "Password",
        inputType: "password",
        placeholder: "password",
      }),
    );
}

function urlField(defaultUrl: string, label = "URL") {
  return z
    .string()
    .nonempty()
    .default(defaultUrl)
    .describe(
      FieldOptions.of({ 
        label, 
        placeholder: defaultUrl 
      })
    );
}

function usernameField(optional = false) {
  const field = z
    .string()
    .describe(FieldOptions.of({ 
      label: optional ? "Username (optional)" : "Username", 
      placeholder: "username" 
    }));
  
  return optional ? field.optional() : field.nonempty();
}

export const PrometheusConnectionSchema = z
  .object({
    type: z.literal("prometheus"),
    url: urlField("http://localhost:9090"),
    username: usernameField(true),
    password: passwordField().describe(
      FieldOptions.of({ label: "Password (optional)" })
    ),
  })
  .describe(FieldOptions.of({ direction: "two-columns" }));

export const LokiConnectionSchema = z
  .object({
    type: z.literal("loki"),
    url: urlField("http://localhost:3100"),
    username: usernameField(true),
    password: passwordField().describe(
      FieldOptions.of({ label: "Password (optional)" })
    ),
  })
  .describe(FieldOptions.of({ direction: "two-columns" }));

export const GrafanaConnectionSchema = z
  .object({
    type: z.literal("grafana"),
    url: urlField("http://localhost:3000"),
    username: usernameField(true),
    password: passwordField().describe(
      FieldOptions.of({ label: "Password (optional)" })
    ),
    apiKey: z
      .string()
      .optional()
      .describe(
        FieldOptions.of({
          label: "API Key (optional)",
          inputType: "password",
        }),
      ),
  })
  .describe(FieldOptions.of({ direction: "two-columns" }));

export const ObservabilityConnectionSchema = z.discriminatedUnion("type", [
  PrometheusConnectionSchema,
  LokiConnectionSchema,
  GrafanaConnectionSchema,
]);

export type ObservabilityConnection = z.infer<typeof ObservabilityConnectionSchema>;
export type PrometheusConnection = z.infer<typeof PrometheusConnectionSchema>;
export type LokiConnection = z.infer<typeof LokiConnectionSchema>;
export type GrafanaConnection = z.infer<typeof GrafanaConnectionSchema>; 