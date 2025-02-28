#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import marimo

__generated_with = "0.10.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import os
    import pandas as pd
    from datetime import datetime, timedelta
    from marimo._observability import promql, logql, grafana_dashboard
    return (mo, os, pd, datetime, timedelta, promql, logql, grafana_dashboard)


@app.cell
def _(mo):
    _ = mo.md(
        """
        # Incident Investigation Canvas
        
        This example demonstrates how to use the observability integrations to create
        an incident investigation canvas. It combines Prometheus metrics, Loki logs,
        and Grafana dashboards to provide a comprehensive view of system behavior during
        an incident.
        """
    )
    return (_,)


@app.cell
def _(mo, os):
    # Configuration
    prometheus_url = mo.ui.text(
        value=os.environ.get("PROMETHEUS_URL", "http://localhost:9090"),
        label="Prometheus URL"
    )
    
    loki_url = mo.ui.text(
        value=os.environ.get("LOKI_URL", "http://localhost:3100"),
        label="Loki URL"
    )
    
    grafana_url = mo.ui.text(
        value=os.environ.get("GRAFANA_URL", "http://localhost:3000"),
        label="Grafana URL"
    )
    return (prometheus_url, loki_url, grafana_url)


@app.cell
def _(mo, datetime, timedelta):
    # Time range selection for the investigation
    incident_time_range = mo.ui.date_range(
        value=(
            (datetime.now() - timedelta(hours=6)).date(),
            datetime.now().date()
        ),
        label="Incident Time Range"
    )
    
    services = mo.ui.multiselect(
        options=[
            "api-gateway", 
            "auth-service", 
            "payment-service", 
            "user-service",
            "inventory-service",
            "notification-service"
        ],
        value=["api-gateway", "auth-service"],
        label="Services to Investigate"
    )
    return (incident_time_range, services)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Incident Investigation
        
        This canvas helps you investigate incidents by providing a unified view of metrics, 
        logs, and dashboards. Start by setting the time range and selecting the services 
        to investigate.
        """
    )
    return (_,)


@app.cell
def _(mo, datetime, incident_time_range):
    def get_time_params():
        # Convert selected time range to parameters for queries
        start_date, end_date = incident_time_range.value
        
        # Convert date to datetime for proper formatting
        start_time = datetime.combine(start_date, datetime.min.time())
        end_time = datetime.combine(end_date, datetime.max.time())
        
        # Format for PromQL/LogQL
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Calculate duration for relative queries
        duration = end_time - start_time
        hours = int(duration.total_seconds() / 3600)
        minutes = int((duration.total_seconds() % 3600) / 60)
        
        relative_time = f"{hours}h"
        if minutes > 0:
            relative_time += f"{minutes}m"
        
        return {
            "start": start_str,
            "end": end_str,
            "relative": relative_time
        }
    
    time_params = get_time_params()
    return (get_time_params, time_params)


@app.cell
def _(mo, promql, prometheus_url, time_params, services):
    def incident_overview():
        # Create a dashboard of key metrics during the incident
        
        # Error rate query
        error_rate_query = f"""
        # @description: Error Rate by Service
        # @start_time: {time_params["start"]}
        # @end_time: {time_params["end"]}
        # @step: 30s
        
        sum(rate(http_server_requests_total{{status=~"5.."}}[5m])) by (service) 
        / 
        sum(rate(http_server_requests_total[5m])) by (service) * 100
        """
        
        try:
            error_rate = promql(
                error_rate_query,
                url=prometheus_url.value,
                output=False  # Don't display yet
            )
            
            # Filter for selected services
            error_rate = error_rate[error_rate['metric'].isin(services.value)]
            
            # Request latency
            latency_query = f"""
            # @description: Request Latency by Service
            # @start_time: {time_params["start"]}
            # @end_time: {time_params["end"]}
            # @step: 30s
            
            histogram_quantile(0.95, sum(rate(http_server_requests_seconds_bucket[5m])) by (service, le))
            """
            
            latency = promql(
                latency_query,
                url=prometheus_url.value,
                output=False
            )
            
            # Filter for selected services
            latency = latency[latency['metric'].isin(services.value)]
            
            # Create a dashboard layout
            return mo.vstack([
                mo.md("### Incident Overview: Key Metrics"),
                mo.hstack([
                    mo.vstack([
                        mo.md("#### Error Rate (%)"),
                        mo.ui.altair_chart(
                            mo.ui.altair_chart._prepare_chart(error_rate, "time", "value", color="metric")
                        )
                    ], width="50%"),
                    mo.vstack([
                        mo.md("#### Request Latency (95th percentile)"),
                        mo.ui.altair_chart(
                            mo.ui.altair_chart._prepare_chart(latency, "time", "value", color="metric")
                        )
                    ], width="50%")
                ])
            ])
        except Exception as e:
            return mo.md(f"Error loading incident overview: {str(e)}")
    
    overview = incident_overview()
    return (incident_overview, overview)


@app.cell
def _(mo, promql, prometheus_url, time_params, services):
    def resource_usage():
        # Resource usage metrics (CPU, Memory)
        
        # CPU usage query
        cpu_query = f"""
        # @description: CPU Usage by Service
        # @start_time: {time_params["start"]}
        # @end_time: {time_params["end"]}
        # @step: 30s
        
        sum(rate(process_cpu_seconds_total[5m])) by (service) * 100
        """
        
        try:
            cpu_usage = promql(
                cpu_query,
                url=prometheus_url.value,
                output=False
            )
            
            # Filter for selected services
            cpu_usage = cpu_usage[cpu_usage['metric'].isin(services.value)]
            
            # Memory usage
            memory_query = f"""
            # @description: Memory Usage by Service
            # @start_time: {time_params["start"]}
            # @end_time: {time_params["end"]}
            # @step: 30s
            
            sum(process_resident_memory_bytes) by (service) / (1024 * 1024)
            """
            
            memory_usage = promql(
                memory_query,
                url=prometheus_url.value,
                output=False
            )
            
            # Filter for selected services
            memory_usage = memory_usage[memory_usage['metric'].isin(services.value)]
            
            # Create a dashboard layout
            return mo.vstack([
                mo.md("### Resource Usage"),
                mo.hstack([
                    mo.vstack([
                        mo.md("#### CPU Usage (%)"),
                        mo.ui.altair_chart(
                            mo.ui.altair_chart._prepare_chart(cpu_usage, "time", "value", color="metric")
                        )
                    ], width="50%"),
                    mo.vstack([
                        mo.md("#### Memory Usage (MB)"),
                        mo.ui.altair_chart(
                            mo.ui.altair_chart._prepare_chart(memory_usage, "time", "value", color="metric")
                        )
                    ], width="50%")
                ])
            ])
        except Exception as e:
            return mo.md(f"Error loading resource usage: {str(e)}")
    
    resources = resource_usage()
    return (resource_usage, resources)


@app.cell
def _(mo, logql, loki_url, time_params, services):
    def error_logs():
        # Error logs from Loki
        service_selector = '{' + ' or '.join([f'service="{s}"' for s in services.value]) + '}'
        
        error_query = f"""
        # @description: Error Logs
        # @start_time: {time_params["start"]}
        # @end_time: {time_params["end"]}
        # @limit: 100
        
        {service_selector} |= "error" | json
        """
        
        try:
            logs = logql(
                error_query,
                url=loki_url.value
            )
            
            return mo.vstack([
                mo.md("### Error Logs"),
                mo.vstack([
                    mo.ui.dataframe(logs, page_size=10, pagination=True)
                ])
            ])
        except Exception as e:
            return mo.md(f"Error loading logs: {str(e)}")
    
    logs_display = error_logs()
    return (error_logs, logs_display)


@app.cell
def _(mo, grafana_dashboard, grafana_url, time_params):
    def service_dependencies():
        # Embed a service dependency dashboard from Grafana
        dashboard_content = f"""
        # @dashboard: service-dependencies
        # @from: {time_params["start"]}
        # @to: {time_params["end"]}
        """
        
        try:
            return mo.vstack([
                mo.md("### Service Dependencies"),
                grafana_dashboard(
                    content=dashboard_content,
                    url=grafana_url.value,
                    height="400px"
                )
            ])
        except Exception as e:
            return mo.md(f"Error loading service dependencies: {str(e)}")
    
    dependencies = service_dependencies()
    return (service_dependencies, dependencies)


@app.cell
def _(mo, pd, logql, loki_url, time_params, services):
    def log_frequency_analysis():
        # Analyze log frequency over time
        service_selector = '{' + ' or '.join([f'service="{s}"' for s in services.value]) + '}'
        
        log_query = f"""
        # @description: All Logs
        # @start_time: {time_params["start"]}
        # @end_time: {time_params["end"]}
        # @limit: 5000
        
        {service_selector}
        """
        
        try:
            logs = logql(
                log_query,
                url=loki_url.value,
                output=False
            )
            
            # Extract timestamp and convert to pandas datetime
            logs['timestamp'] = pd.to_datetime(logs['timestamp'])
            
            # Extract log level if available
            if 'level' in logs.columns:
                level_col = 'level'
            elif 'log_level' in logs.columns:
                level_col = 'log_level'
            else:
                # Add a default level based on content
                def determine_level(message):
                    message = str(message).lower()
                    if 'error' in message or 'exception' in message or 'fail' in message:
                        return 'ERROR'
                    elif 'warn' in message:
                        return 'WARN'
                    else:
                        return 'INFO'
                
                logs['level'] = logs['message'].apply(determine_level)
                level_col = 'level'
            
            # Ensure level is uppercase for consistency
            logs[level_col] = logs[level_col].str.upper()
            
            # Group by timestamp (10-minute buckets) and level
            logs['time_bucket'] = logs['timestamp'].dt.floor('10T')
            frequency = logs.groupby(['time_bucket', level_col, 'service']).size().reset_index(name='count')
            
            # Prepare for visualization
            pivoted = frequency.pivot_table(
                index=['time_bucket', 'service'], 
                columns=level_col, 
                values='count', 
                fill_value=0
            ).reset_index()
            
            # Melt back to long format for plotting
            log_data = pd.melt(
                pivoted, 
                id_vars=['time_bucket', 'service'], 
                var_name='level', 
                value_name='count'
            )
            
            # Create visualizations
            return mo.vstack([
                mo.md("### Log Frequency Analysis"),
                mo.hstack([
                    mo.vstack([
                        mo.md("#### Log Frequency by Level"),
                        mo.ui.altair_chart(
                            mo.ui.altair_chart._prepare_chart(
                                log_data, 
                                x="time_bucket", 
                                y="count", 
                                color="level",
                                column="service",
                                chart_type="bar"
                            )
                        )
                    ]),
                    mo.vstack([
                        mo.md("#### Log Level Distribution"),
                        mo.ui.altair_chart(
                            mo.ui.altair_chart._prepare_chart(
                                log_data.groupby(['service', 'level'])['count'].sum().reset_index(),
                                x="level",
                                y="count",
                                color="level",
                                column="service",
                                chart_type="bar"
                            )
                        )
                    ])
                ])
            ])
        except Exception as e:
            return mo.md(f"Error analyzing logs: {str(e)}")
    
    log_analysis = log_frequency_analysis()
    return (log_frequency_analysis, log_analysis)


@app.cell
def _(mo, pd, promql, logql, prometheus_url, loki_url, time_params, services):
    def timeline_correlation():
        # Correlate metrics and logs on a timeline
        try:
            # Get error rate metrics
            error_rate_query = f"""
            # @description: Error Rate
            # @start_time: {time_params["start"]}
            # @end_time: {time_params["end"]}
            # @step: 30s
            
            sum(rate(http_server_requests_total{{status=~"5.."}}[5m])) by (service) 
            / 
            sum(rate(http_server_requests_total[5m])) by (service) * 100
            """
            
            error_metrics = promql(
                error_rate_query,
                url=prometheus_url.value,
                output=False
            )
            error_metrics = error_metrics[error_metrics['metric'].isin(services.value)]
            
            # Get error logs
            service_selector = '{' + ' or '.join([f'service="{s}"' for s in services.value]) + '}'
            error_log_query = f"""
            # @description: Error Logs
            # @start_time: {time_params["start"]}
            # @end_time: {time_params["end"]}
            # @limit: 1000
            
            {service_selector} |= "error" | json
            """
            
            error_logs = logql(
                error_log_query,
                url=loki_url.value,
                output=False
            )
            
            # Ensure proper timestamp format for both datasets
            error_metrics['time'] = pd.to_datetime(error_metrics['time'])
            error_logs['timestamp'] = pd.to_datetime(error_logs['timestamp'])
            
            # Function to get normalized timestamps for comparison
            def get_timestamp_col(df):
                if 'time' in df.columns:
                    return 'time'
                elif 'timestamp' in df.columns:
                    return 'timestamp'
                else:
                    # If neither exists, create a new one
                    df['timestamp'] = pd.to_datetime(df.index)
                    return 'timestamp'
            
            # Create a correlation timeline
            metrics_time_col = get_timestamp_col(error_metrics)
            logs_time_col = get_timestamp_col(error_logs)
            
            # Create error metric time series
            metrics_plot = mo.ui.altair_chart(
                mo.ui.altair_chart._prepare_chart(
                    error_metrics, 
                    x=metrics_time_col, 
                    y="value", 
                    color="metric"
                )
            )
            
            # Create error logs timeline (event markers)
            if not error_logs.empty:
                # Group logs by minute
                error_logs['minute'] = error_logs[logs_time_col].dt.floor('1min')
                log_count = error_logs.groupby(['minute', 'service']).size().reset_index(name='error_count')
                log_count.rename(columns={'minute': 'time'}, inplace=True)
                
                logs_plot = mo.ui.altair_chart(
                    mo.ui.altair_chart._prepare_chart(
                        log_count, 
                        x="time", 
                        y="error_count", 
                        color="service",
                        chart_type="bar"
                    )
                )
            else:
                logs_plot = mo.md("No error logs found in the selected time range")
            
            # Combine into a layout
            return mo.vstack([
                mo.md("### Timeline Correlation"),
                mo.hstack([
                    mo.vstack([
                        mo.md("#### Error Rate (%)"),
                        metrics_plot
                    ]),
                    mo.vstack([
                        mo.md("#### Error Log Frequency"),
                        logs_plot
                    ])
                ])
            ])
        except Exception as e:
            return mo.md(f"Error generating correlation timeline: {str(e)}")
    
    timeline = timeline_correlation()
    return (timeline_correlation, timeline)


@app.cell
def _(mo, pd, datetime, services, time_params, timeline_correlation, incident_overview, 
      resource_usage, error_logs, log_frequency_analysis):
    def generate_incident_report():
        # Generate a markdown report summarizing findings
        
        start_time, end_time = time_params["start"], time_params["end"]
        
        # Parse ISO format strings to datetime objects
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration_mins = int((end_dt - start_dt).total_seconds() / 60)
        except Exception:
            # Fallback if parsing fails
            duration_mins = 0
        
        report = f"""
        # Incident Investigation Report
        
        ## Summary
        
        - **Services Affected**: {", ".join(services.value)}
        - **Incident Time**: {start_time} to {end_time}
        - **Duration**: {duration_mins} minutes
        
        ## Key Findings
        
        These are automatically generated findings based on the analysis. Please review and edit as needed.
        
        - Observed elevated error rates for the following services: {", ".join(services.value)}
        - Resource usage patterns show...
        - Log analysis indicates...
        
        ## Next Steps
        
        1. Review detailed error logs for root cause
        2. Check recent deployments or configuration changes
        3. Implement monitoring for the identified failure patterns
        4. Update runbooks with new troubleshooting steps
        
        ## Attachments
        
        - Metrics dashboard
        - Error logs
        - Timeline correlation
        """
        
        return mo.md(report)
    
    report = generate_incident_report()
    return (generate_incident_report, report)


if __name__ == "__main__":
    app.run()