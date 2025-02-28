#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import marimo

__generated_with = "0.10.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import os
    from marimo._observability import grafana_dashboard
    return (mo, os, grafana_dashboard)


@app.cell
def _(mo):
    _ = mo.md(
        """
        # Grafana Dashboard Integration Example
        
        This example demonstrates how to embed Grafana dashboards in Marimo notebooks.
        """
    )
    return (_,)


@app.cell
def _(mo, os):
    grafana_url = mo.ui.text(
        value=os.environ.get("GRAFANA_URL", "http://localhost:3000"),
        label="Grafana URL",
        placeholder="Enter your Grafana URL"
    )
    return (grafana_url,)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Embedding a Grafana Dashboard
        
        Using the `grafana_dashboard` function to embed a Grafana dashboard.
        """
    )
    return (_,)


@app.cell
def _(mo):
    dashboard_uid = mo.ui.text(
        value="rYdddlPWk",  # Example UID for Node Exporter dashboard
        label="Dashboard UID",
        placeholder="Enter dashboard UID"
    )
    
    time_range = mo.ui.dropdown(
        options=[
            "15m", "30m", "1h", "3h", "6h", "12h", "24h", "2d", "7d", "30d"
        ],
        value="6h",
        label="Time Range"
    )
    
    refresh_rate = mo.ui.dropdown(
        options=[
            "off", "5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"
        ],
        value="off",
        label="Refresh Rate"
    )
    
    dashboard_theme = mo.ui.radio(
        options=["light", "dark"],
        value="light",
        label="Dashboard Theme"
    )
    
    dashboard_height = mo.ui.slider(
        start=300,
        stop=1000,
        step=50,
        value=500,
        label="Dashboard Height (px)"
    )
    return (dashboard_uid, time_range, refresh_rate, dashboard_theme, dashboard_height)


@app.cell
def _(mo, grafana_dashboard, grafana_url, dashboard_uid, time_range, dashboard_theme, refresh_rate, dashboard_height):
    def display_dashboard():
        # Create dashboard embed with user-selected options
        dashboard_content = f"""
        # @dashboard: {dashboard_uid.value}
        # @from: now-{time_range.value}
        # @to: now
        # @var-instance: All
        """
        
        return grafana_dashboard(
            content=dashboard_content,
            url=grafana_url.value,
            theme=dashboard_theme.value,
            refresh=refresh_rate.value,
            height=f"{dashboard_height.value}px"
        )
    
    dashboard = display_dashboard()
    return (display_dashboard, dashboard)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Embedding Multiple Panels
        
        You can embed multiple panels from different dashboards for a custom view.
        """
    )
    return (_,)


@app.cell
def _(mo, grafana_dashboard, grafana_url):
    def display_multi_panel():
        # Create layout for multiple dashboard panels using hstack and vstack
        return mo.hstack([
            mo.vstack([
                mo.md("### CPU Usage"),
                grafana_dashboard(
                    content="# @dashboard: rYdddlPWk\n# @from: now-1h\n# @to: now\n# @var-instance: All",
                    url=grafana_url.value,
                    height="250px"
                )
            ]),
            mo.vstack([
                mo.md("### Memory Usage"),
                grafana_dashboard(
                    content="# @dashboard: rYdddlPWk\n# @from: now-1h\n# @to: now\n# @var-instance: All",
                    url=grafana_url.value,
                    height="250px"
                )
            ])
        ])
    
    multi_panel = display_multi_panel()
    return (display_multi_panel, multi_panel)


@app.cell
def _(mo):
    _ = mo.md(
        """
        ## Custom Dashboard Integration
        
        You can create custom dashboards that combine Grafana panels with Marimo UI elements
        and PromQL/LogQL queries for a fully integrated observability experience.
        """
    )
    return (_,)


@app.cell
def _(mo, grafana_dashboard, grafana_url):
    def custom_dashboard():
        from marimo._observability import promql
        
        # Query CPU metrics directly with PromQL
        cpu_query = """
        # @description: CPU Usage
        # @start_time: -1h
        # @step: 15s
        
        avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100
        """
        
        cpu_metrics = promql(
            cpu_query,
            url="http://localhost:9090",  # Prometheus URL
            output=False  # Don't display visualization yet
        )
        
        # Create custom dashboard layout
        return mo.vstack([
            mo.md("# System Overview Dashboard"),
            mo.hstack([
                mo.vstack([
                    mo.md("## CPU Metrics"),
                    mo.ui.altair_chart(
                        # Create custom CPU chart from PromQL data
                        mo.ui.altair_chart._prepare_chart(cpu_metrics, "time", "value", color="metric")
                    ),
                ], width="50%"),
                mo.vstack([
                    mo.md("## Memory Dashboard"),
                    grafana_dashboard(
                        content="# @dashboard: rYdddlPWk\n# @from: now-1h\n# @to: now",
                        url=grafana_url.value,
                        height="300px"
                    )
                ], width="50%")
            ])
        ])
    
    dashboard = custom_dashboard()
    return (custom_dashboard, dashboard)


if __name__ == "__main__":
    app.run()