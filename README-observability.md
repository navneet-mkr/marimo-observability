# Marimo Observability: AI-Powered Incident Investigation Canvas

This project extends the [Marimo notebook framework](https://github.com/marimo-team/marimo) to create an AI-driven incident management and investigation canvas. It transforms how engineering teams troubleshoot production issues by integrating observability tools, AI analysis, and collaborative investigation capabilities into an interactive notebook environment.

## Features

### Current Implementation: Grafana Stack Integration

This initial implementation focuses on integrating with the Grafana observability stack:

1. **PromQL Integration**
   - Execute and visualize Prometheus queries
   - Support for time ranges, step sizes, and metadata
   - Interactive time series visualizations
   - Data export for further analysis

2. **LogQL Integration**
   - Query and display Loki logs with syntax highlighting
   - JSON log parsing
   - Log frequency visualizations
   - Support for log-based metrics

3. **Grafana Dashboard Embedding**
   - Embed existing dashboards
   - Control time ranges and variables
   - Create custom layouts with multiple panels

### Coming Soon

Future updates will add:

1. **AI-Assisted Analysis**
   - Automated anomaly detection
   - Root cause suggestions
   - Query recommendations
   - Natural language query translation

2. **Collaborative Features**
   - Real-time collaboration
   - Incident timelines
   - Persistent insights
   - Knowledge base integration

3. **Advanced Integrations**
   - Additional observability tools
   - Incident management systems
   - Documentation generation
   - Alert correlation

## Installation

### Prerequisites

- Python 3.8 or later
- Marimo (`pip install marimo`)
- Access to Prometheus, Loki, and/or Grafana APIs

### Installation Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/marimo-observability.git
   cd marimo-observability
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-observability.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Basic Examples

```python
import marimo as mo
from marimo._observability import promql, logql, grafana_dashboard

# PromQL query
metrics = promql("""
# @description: CPU Usage
# @start_time: -1h
# @step: 15s

avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100
""", url="http://localhost:9090")

# LogQL query
logs = logql("""
# @description: Error Logs
# @start_time: -1h
# @limit: 100

{app="my-service"} |= "error" | json
""", url="http://localhost:3100")

# Grafana dashboard embedding
dashboard = grafana_dashboard("""
# @dashboard: my-dashboard-uid
# @from: now-6h
# @to: now
# @var-instance: server1
""", url="http://localhost:3000")
```

### Example Notebooks

See the `examples/observability` directory for complete examples:

1. **[Prometheus Example](examples/observability/prometheus_example.py)**: Demonstrates PromQL integration
2. **[Loki Example](examples/observability/loki_example.py)**: Demonstrates LogQL integration
3. **[Grafana Example](examples/observability/grafana_example.py)**: Demonstrates Grafana dashboard embedding
4. **[Incident Investigation](examples/observability/incident_investigation.py)**: A complete incident investigation canvas that combines all components

## Configuration

### Environment Variables

- `PROMETHEUS_URL`: URL for Prometheus API
- `LOKI_URL`: URL for Loki API
- `GRAFANA_URL`: URL for Grafana

### Query Metadata Comments

All query functions support metadata comments:

```python
promql("""
# @description: CPU Usage
# @start_time: -1h
# @step: 15s
# @url: http://prometheus.example.com

avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100
""")
```

## Development

### Project Structure

- `marimo/_observability/`: Core module implementation
  - `__init__.py`: Module entry point
  - `promql.py`: Prometheus integration
  - `logql.py`: Loki integration
  - `grafana.py`: Grafana dashboard integration
- `examples/observability/`: Example notebooks
- `requirements-observability.txt`: Dependencies

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add your feature or fix
4. Add tests for your changes
5. Submit a pull request

## License

This project is licensed under the same license as Marimo - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The [Marimo team](https://github.com/marimo-team/marimo) for creating the excellent notebook framework this builds upon
- The Grafana, Prometheus, and Loki projects for their observability tools