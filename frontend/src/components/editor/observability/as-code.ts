/* Copyright 2024 Marimo. All rights reserved. */
import { assertNever } from "@/utils/assertNever";
import { ObservabilityConnectionSchema, type ObservabilityConnection } from "./schemas";

export function generateObservabilityCode(
  connection: ObservabilityConnection,
): string {
  // Parse the connection to ensure it's valid
  ObservabilityConnectionSchema.parse(connection);

  let imports: string[] = [];
  let code = "";
  let authCode = "";

  switch (connection.type) {
    case "prometheus":
      imports = [
        "import os",
        "import pandas as pd",
        "import requests",
        "from marimo._observability.promql import PrometheusClient, TimeRange"
      ];

      code = connection.username && connection.password
        ? `
# Create Prometheus client with auth
username = "${connection.username}"
password = os.environ.get("PROMETHEUS_PASSWORD", "${connection.password}")
prom_client = PrometheusClient(
    url="${connection.url}",
    auth=(username, password)
)

# Example usage:
# time_range = TimeRange(start="-1h")
# df = prom_client.query("up", time_range)
`
        : `
# Create Prometheus client
prom_client = PrometheusClient(url="${connection.url}")

# Example usage:
# time_range = TimeRange(start="-1h")
# df = prom_client.query("up", time_range)
`;
      break;

    case "loki":
      imports = [
        "import os",
        "import pandas as pd",
        "import requests",
        "from marimo._observability.logql import LokiClient, LokiTimeRange"
      ];

      code = connection.username && connection.password
        ? `
# Create Loki client with auth
username = "${connection.username}"
password = os.environ.get("LOKI_PASSWORD", "${connection.password}")
loki_client = LokiClient(
    url="${connection.url}",
    auth=(username, password)
)

# Example usage:
# time_range = LokiTimeRange(start="-1h", limit=100)
# df = loki_client.query('{app="marimo"}', time_range)
`
        : `
# Create Loki client
loki_client = LokiClient(url="${connection.url}")

# Example usage:
# time_range = LokiTimeRange(start="-1h", limit=100)
# df = loki_client.query('{app="marimo"}', time_range)
`;
      break;

    case "grafana":
      imports = [
        "import os",
        "from marimo._observability.grafana import grafana_dashboard"
      ];

      authCode = connection.apiKey 
        ? `# Grafana API key
api_key = os.environ.get("GRAFANA_API_KEY", "${connection.apiKey}")
`
        : connection.username && connection.password
        ? `# Grafana credentials
username = "${connection.username}"
password = os.environ.get("GRAFANA_PASSWORD", "${connection.password}")
`
        : "";

      code = `
${authCode}
# Example usage:
# grafana_dashboard(
#     url="${connection.url}",
#     dashboard="your-dashboard-uid",
#     from_time="-6h",
#     to_time="now",
#     theme="light",
#     height="500px",
#     width="100%"
# )
`;
      break;

    default:
      assertNever(connection);
  }

  return `${imports.join("\n")}\n${code.trim()}`;
} 