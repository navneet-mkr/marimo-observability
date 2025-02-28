#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import marimo

__generated_with = "0.10.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import os
    from marimo._observability import promql
    return (mo, os, promql)


@app.cell
def _(mo):
    _ = mo.md(
        """
        # Prometheus Integration Example
        
        This example demonstrates how to use the custom PromQL cell type to query Prometheus metrics.
        """
    )
    return (_,)


@app.cell
def _(mo, os):
    prometheus_url = mo.ui.text(
        value=os.environ.get("PROMETHEUS_URL", "http://localhost:9090"),
        label="Prometheus URL",
        placeholder="Enter your Prometheus URL"
    )
    return (prometheus_url,)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## PromQL Query Examples
        
        Using the promql function to query Prometheus metrics.
        """
    )
    return (_,)


@app.cell
def _(mo):
    # Basic PromQL query
    _ = mo.md("### Basic PromQL Query")
    return (_,)


@app.cell
def _(mo, promql, prometheus_url):
    basic_query = """
    # @description: CPU Usage
    # @start_time: -1h
    # @step: 15s
    
    avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100
    """
    
    cpu_metrics = promql(
        basic_query,
        url=prometheus_url.value
    )
    return (basic_query, cpu_metrics)


@app.cell
def _(mo):
    _ = mo.md("### Query with Timeframe Selection")
    return (_,)


@app.cell
def _(mo):
    start_time = mo.ui.dropdown(
        options=["1h", "6h", "12h", "24h", "7d"],
        value="1h",
        label="Time Range",
    )
    return (start_time,)


@app.cell
def _(mo, promql, prometheus_url, start_time):
    def get_metrics():
        # Dynamic query with user-selected time range
        query = f"""
        # @description: HTTP Request Rate
        # @start_time: -{start_time.value}
        # @step: 30s
        
        sum(rate(http_requests_total[5m])) by (status_code)
        """
        
        return promql(
            query,
            url=prometheus_url.value
        )
    
    metrics = get_metrics()
    return (get_metrics, metrics)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Using the Results Programmatically
        
        You can work with the returned DataFrame like any other pandas DataFrame.
        """
    )
    return (_,)


@app.cell
def _(mo, cpu_metrics):
    def analyze_metrics():
        import pandas as pd
        
        if isinstance(cpu_metrics, pd.DataFrame) and not cpu_metrics.empty:
            # Calculate some statistics
            stats = {
                "mean": cpu_metrics["value"].mean(),
                "max": cpu_metrics["value"].max(),
                "min": cpu_metrics["value"].min()
            }
            
            # Display stats
            return mo.ui.table({
                "Statistic": list(stats.keys()),
                "Value": list(stats.values())
            })
        else:
            return mo.md("No metrics data available or connection to Prometheus failed")
    
    analysis = analyze_metrics()
    return (analyze_metrics, analysis)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Query Builder
        
        A simple query builder UI for Prometheus metrics.
        """
    )
    return (_,)


@app.cell
def _(mo):
    metric_name = mo.ui.text(
        value="node_cpu_seconds_total",
        label="Metric Name"
    )
    
    label_filter = mo.ui.text(
        value='mode!="idle"',
        label="Label Filter"
    )
    
    aggregation = mo.ui.dropdown(
        options=["None", "sum", "avg", "min", "max"],
        value="avg",
        label="Aggregation"
    )
    
    grouping = mo.ui.text(
        value="instance",
        label="Group By"
    )
    
    rate_interval = mo.ui.text(
        value="5m",
        label="Rate Interval"
    )
    return (metric_name, label_filter, aggregation, grouping, rate_interval)


@app.cell
def _(mo, promql, prometheus_url, metric_name, label_filter, aggregation, grouping, rate_interval):
    def build_query():
        # Build the query based on UI inputs
        base_query = f"{metric_name.value}"
        
        # Add label filters if provided
        if label_filter.value:
            base_query += f"{{{label_filter.value}}}"
        
        # Add rate function if interval provided
        if rate_interval.value:
            base_query = f"rate({base_query}[{rate_interval.value}])"
        
        # Add aggregation if selected
        if aggregation.value != "None":
            if grouping.value:
                base_query = f"{aggregation.value} by ({grouping.value}) ({base_query})"
            else:
                base_query = f"{aggregation.value}({base_query})"
        
        # Multiply by 100 for CPU percentage
        if metric_name.value == "node_cpu_seconds_total":
            base_query += " * 100"
        
        # Create the full query with metadata
        query = f"""
        # @description: {metric_name.value} Query
        # @start_time: -1h
        # @step: 15s
        
        {base_query}
        """
        
        # Display the query
        mo.output.clear()
        mo.output.append(mo.md(f"### Generated Query\n```promql\n{base_query}\n```"))
        
        # Execute the query
        result = promql(
            query,
            url=prometheus_url.value
        )
        
        return result
    
    query_result = build_query()
    return (build_query, query_result)


if __name__ == "__main__":
    app.run()