# Marimo Observability

This module extends Marimo with specialized functionality for observability and incident investigation. It provides:

1. **PromQL Integration**: Query and visualize Prometheus metrics
2. **LogQL Integration**: Query and visualize Loki logs
3. **Grafana Dashboard Integration**: Embed Grafana dashboards in notebooks

## Getting Started

To use the observability features, you need to have access to Prometheus, Loki, and/or Grafana.

```python
import marimo as mo
from marimo._observability import promql, logql, grafana_dashboard
```

## PromQL Usage

Execute PromQL queries against Prometheus:

```python
# Execute a PromQL query with metadata in comments
metrics = promql.promql("""
# @description: CPU Usage
# @start_time: -1h
# @step: 15s

avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100
""", url="http://localhost:9090")

# Access the returned data
print(metrics.head())
```

## LogQL Usage

Execute LogQL queries against Loki:

```python
# Execute a LogQL query with metadata in comments
logs = logql.logql("""
# @description: Error Logs
# @start_time: -1h
# @limit: 100

{app="my-service"} |= "error" | json
""", url="http://localhost:3100")

# Access the returned data
print(logs.head())
```

## Grafana Dashboard Embedding

Embed Grafana dashboards in notebooks:

```python
# Embed a Grafana dashboard with metadata in comments
dashboard = grafana_dashboard("""
# @dashboard: my-dashboard-uid
# @from: now-6h
# @to: now
# @var-instance: server1
""", url="http://localhost:3000")
```

## Example Notebooks

1. **[Prometheus Example](prometheus_example.py)**: Demonstrates PromQL integration
2. **[Loki Example](loki_example.py)**: Demonstrates LogQL integration
3. **[Grafana Example](grafana_example.py)**: Demonstrates Grafana dashboard embedding
4. **[Incident Investigation](incident_investigation.py)**: A complete incident investigation canvas that combines all components

## Configuration

You can configure the observability components using:

1. **Environment Variables**:
   - `PROMETHEUS_URL`: URL for Prometheus API
   - `LOKI_URL`: URL for Loki API 
   - `GRAFANA_URL`: URL for Grafana

2. **Query Comments**:
   - Use comments like `# @start_time: -1h` to set query parameters
   - See examples for complete syntax

3. **Direct Parameters**:
   - Pass parameters directly to functions

## Features

### PromQL Integration

- Execute PromQL queries with time ranges and step sizes
- Automatic visualization of time series data
- Support for different result types (matrix, vector, scalar)
- Interactive charts with Altair
- Dataframe representation for further analysis

### LogQL Integration

- Execute LogQL queries with time ranges and limits
- Automatic parsing of JSON logs
- Log frequency visualization
- Support for log-based metrics queries
- Interactive displays with syntax highlighting

### Grafana Dashboard Integration

- Embed existing Grafana dashboards
- Control dashboard parameters (time range, variables, theme)
- Combine multiple dashboard panels
- Create custom layouts with Marimo UI components