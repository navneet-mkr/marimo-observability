#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import marimo

__generated_with = "0.10.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import os
    from marimo._observability import logql
    return (mo, os, logql)


@app.cell
def _(mo):
    _ = mo.md(
        """
        # Loki Integration Example
        
        This example demonstrates how to use the custom LogQL cell type to query Loki logs.
        """
    )
    return (_,)


@app.cell
def _(mo, os):
    loki_url = mo.ui.text(
        value=os.environ.get("LOKI_URL", "http://localhost:3100"),
        label="Loki URL",
        placeholder="Enter your Loki URL"
    )
    return (loki_url,)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## LogQL Query Examples
        
        Using the logql function to query Loki logs.
        """
    )
    return (_,)


@app.cell
def _(mo):
    # Basic LogQL query
    _ = mo.md("### Basic LogQL Query")
    return (_,)


@app.cell
def _(mo, logql, loki_url):
    basic_query = """
    # @description: Error Logs
    # @start_time: -1h
    # @limit: 100
    
    {app="my-service"} |= "error" | json
    """
    
    error_logs = logql(
        basic_query,
        url=loki_url.value
    )
    return (basic_query, error_logs)


@app.cell
def _(mo):
    _ = mo.md("### Query with Timeframe Selection")
    return (_,)


@app.cell
def _(mo):
    time_range = mo.ui.dropdown(
        options=["15m", "30m", "1h", "6h", "12h", "24h"],
        value="1h",
        label="Time Range",
    )
    
    log_limit = mo.ui.slider(
        start=10,
        stop=1000,
        step=10,
        value=100,
        label="Log Limit"
    )
    return (time_range, log_limit)


@app.cell
def _(mo, logql, loki_url, time_range, log_limit):
    def get_logs():
        # Dynamic query with user-selected time range and limit
        query = f"""
        # @description: Recent Logs
        # @start_time: -{time_range.value}
        # @limit: {log_limit.value}
        
        {{app="my-service"}}
        """
        
        return logql(
            query,
            url=loki_url.value
        )
    
    logs = get_logs()
    return (get_logs, logs)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Log Analysis Examples
        
        Using LogQL to perform log analysis.
        """
    )
    return (_,)


@app.cell
def _(mo):
    _ = mo.md("### Error Rate Query")
    return (_,)


@app.cell
def _(mo, logql, loki_url):
    error_rate_query = """
    # @description: Error Rate
    # @start_time: -6h
    
    sum(rate({app="my-service"} |= "error" [5m])) / sum(rate({app="my-service"}[5m])) * 100
    """
    
    error_rate = logql(
        error_rate_query,
        url=loki_url.value
    )
    return (error_rate_query, error_rate)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Log Query Builder
        
        A simple query builder UI for Loki logs.
        """
    )
    return (_,)


@app.cell
def _(mo):
    app_name = mo.ui.text(
        value="my-service",
        label="Application Name"
    )
    
    log_filter = mo.ui.text(
        value="error",
        label="Filter Term (optional)"
    )
    
    use_json = mo.ui.checkbox(
        value=True,
        label="Parse as JSON"
    )
    return (app_name, log_filter, use_json)


@app.cell
def _(mo, logql, loki_url, time_range, log_limit, app_name, log_filter, use_json):
    def build_log_query():
        # Build the query based on UI inputs
        label_selector = f'{{app="{app_name.value}"}}'
        
        # Add filter if provided
        if log_filter.value:
            label_selector += f' |= "{log_filter.value}"'
        
        # Add JSON parser if selected
        if use_json.value:
            label_selector += " | json"
        
        # Create the full query with metadata
        query = f"""
        # @description: Logs for {app_name.value}
        # @start_time: -{time_range.value}
        # @limit: {log_limit.value}
        
        {label_selector}
        """
        
        # Display the query
        mo.output.clear()
        mo.output.append(mo.md(f"### Generated Query\n```logql\n{label_selector}\n```"))
        
        # Execute the query
        result = logql(
            query,
            url=loki_url.value
        )
        
        return result
    
    query_result = build_log_query()
    return (build_log_query, query_result)


if __name__ == "__main__":
    app.run()