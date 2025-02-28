"""PromQL integration for Marimo.

This module provides functions for executing PromQL queries against Prometheus
and visualizing the results.
"""

import re
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import urllib.parse

import pandas as pd
import requests
from pydantic import BaseModel

import marimo as mo
from marimo._output.hypertext import Html


class TimeRange(BaseModel):
    """Time range for PromQL queries."""
    
    start: Union[str, datetime]
    end: Union[str, datetime, None] = None
    step: Union[str, int, float, None] = None
    
    def to_prometheus_params(self) -> Dict[str, str]:
        """Convert time range to Prometheus API parameters."""
        params = {}
        
        # Handle start time
        if isinstance(self.start, datetime):
            params["start"] = self.start.timestamp().__str__()
        elif self.start.startswith("-") and self.start.endswith(("s", "m", "h", "d", "w", "y")):
            # Relative time like -1h
            offset = self._parse_relative_time(self.start)
            params["start"] = (datetime.now() - offset).timestamp().__str__()
        else:
            params["start"] = self.start
            
        # Handle end time
        if self.end is None:
            params["end"] = datetime.now().timestamp().__str__()
        elif isinstance(self.end, datetime):
            params["end"] = self.end.timestamp().__str__()
        else:
            params["end"] = self.end
            
        # Handle step
        if self.step is not None:
            if isinstance(self.step, (int, float)):
                # Convert seconds to string
                params["step"] = str(self.step)
            else:
                # Convert string like "15s" to seconds
                match = re.match(r"(\d+)([smhd])", self.step)
                if match:
                    value, unit = match.groups()
                    seconds = self._convert_to_seconds(int(value), unit)
                    params["step"] = str(seconds)
                else:
                    params["step"] = self.step
        
        return params
    
    def _parse_relative_time(self, time_str: str) -> timedelta:
        """Parse relative time string like -1h to timedelta."""
        match = re.match(r"-(\d+)([smhdwy])", time_str)
        if not match:
            raise ValueError(f"Invalid relative time format: {time_str}")
        
        value, unit = match.groups()
        value = int(value)
        
        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
        elif unit == "w":
            return timedelta(weeks=value)
        elif unit == "y":
            return timedelta(days=value*365)
        else:
            raise ValueError(f"Unknown time unit: {unit}")
    
    def _convert_to_seconds(self, value: int, unit: str) -> int:
        """Convert time unit to seconds."""
        if unit == "s":
            return value
        elif unit == "m":
            return value * 60
        elif unit == "h":
            return value * 3600
        elif unit == "d":
            return value * 86400
        else:
            raise ValueError(f"Unknown time unit: {unit}")


class PrometheusClient:
    """Client for Prometheus API."""
    
    def __init__(self, url: str, timeout: int = 30, auth: Optional[Tuple[str, str]] = None):
        """Initialize Prometheus client.
        
        Args:
            url: Prometheus API URL
            timeout: Request timeout in seconds
            auth: Optional (username, password) tuple for basic auth
        """
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.auth = auth
        self.session = requests.Session()
        
    def query(self, query: str, time_range: TimeRange) -> Dict[str, Any]:
        """Execute a PromQL query."""
        endpoint = f"{self.url}/api/v1/query_range"
        
        params = time_range.to_prometheus_params()
        params["query"] = query
        
        response = self.session.get(
            endpoint,
            params=params,
            timeout=self.timeout,
            auth=self.auth
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_metric_names(self) -> List[str]:
        """Get available metric names."""
        endpoint = f"{self.url}/api/v1/label/__name__/values"
        
        response = self.session.get(
            endpoint,
            timeout=self.timeout,
            auth=self.auth
        )
        
        response.raise_for_status()
        return response.json().get("data", [])


class ResultType(str, Enum):
    """Prometheus result types."""
    
    MATRIX = "matrix"
    VECTOR = "vector"
    SCALAR = "scalar"
    STRING = "string"


def _extract_metadata_from_comments(query: str) -> Dict[str, Any]:
    """Extract metadata from query comments.
    
    Handles comments like:
    # @start_time: -6h
    # @step: 15s
    # @description: API Error Rate
    """
    metadata = {}
    
    # Match comments that have @key: value format
    pattern = r"#\s*@([a-zA-Z_]+):\s*(.+)$"
    
    for line in query.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            key, value = match.groups()
            metadata[key] = value.strip()
    
    return metadata


def _convert_prometheus_result_to_df(result: Dict[str, Any]) -> pd.DataFrame:
    """Convert Prometheus API result to pandas DataFrame."""
    result_type = result.get("resultType")
    data = result.get("result", [])
    
    if not data:
        return pd.DataFrame()
    
    if result_type == ResultType.MATRIX:
        # Time series data
        frames = []
        
        for series in data:
            metric = series.get("metric", {})
            metric_name = metric.get("__name__", "value")
            
            # Create labels string
            labels = ", ".join([f'{k}="{v}"' for k, v in metric.items() if k != "__name__"])
            series_name = f"{metric_name}{{{labels}}}" if labels else metric_name
            
            # Convert values to dataframe
            values = series.get("values", [])
            if values:
                times, values = zip(*values)
                df = pd.DataFrame({
                    "time": pd.to_datetime(times, unit="s"),
                    "value": values,
                    "metric": series_name
                })
                frames.append(df)
        
        if frames:
            return pd.concat(frames, ignore_index=True)
        return pd.DataFrame()
    
    elif result_type == ResultType.VECTOR:
        # Instant vector
        rows = []
        
        for point in data:
            metric = point.get("metric", {})
            metric_name = metric.get("__name__", "value")
            
            # Create labels string
            labels = ", ".join([f'{k}="{v}"' for k, v in metric.items() if k != "__name__"])
            series_name = f"{metric_name}{{{labels}}}" if labels else metric_name
            
            # Extract timestamp and value
            value = point.get("value", [])
            if len(value) == 2:
                timestamp, val = value
                rows.append({
                    "time": pd.to_datetime(timestamp, unit="s"),
                    "value": val,
                    "metric": series_name
                })
        
        if rows:
            return pd.DataFrame(rows)
        return pd.DataFrame()
    
    elif result_type in (ResultType.SCALAR, ResultType.STRING):
        # Single value
        timestamp, value = result.get("result", [0, ""])
        return pd.DataFrame({
            "time": [pd.to_datetime(timestamp, unit="s")],
            "value": [value],
            "metric": ["scalar"]
        })
    
    return pd.DataFrame()


def promql(
    query: str,
    url: Optional[str] = None,
    auth: Optional[Tuple[str, str]] = None,
    time_range: Optional[TimeRange] = None,
    output: bool = True
) -> pd.DataFrame:
    """Execute a PromQL query and return the results.
    
    Args:
        query: PromQL query string (may include metadata comments)
        url: Prometheus API URL (if None, uses environment variable PROMETHEUS_URL)
        auth: Optional (username, password) tuple for basic auth
        time_range: Optional time range for the query
        output: Whether to display results as a visualization
    
    Returns:
        DataFrame with query results
    """
    import os
    
    # Extract metadata from query comments
    metadata = _extract_metadata_from_comments(query)
    
    # Clean query by removing metadata comments
    clean_query = "\n".join(
        line for line in query.split("\n") 
        if not re.match(r"#\s*@[a-zA-Z_]+:", line.strip())
    ).strip()
    
    # Get URL from params, metadata, or environment
    if url is None:
        url = metadata.get("url") or os.environ.get("PROMETHEUS_URL")
        if url is None:
            raise ValueError(
                "Prometheus URL not provided. Either set the PROMETHEUS_URL "
                "environment variable, include a # @url: comment, or pass the url parameter."
            )
    
    # Create time range if not provided
    if time_range is None:
        start_time = metadata.get("start_time", "-1h")
        end_time = metadata.get("end_time")
        step = metadata.get("step")
        
        time_range = TimeRange(
            start=start_time,
            end=end_time,
            step=step
        )
    
    # Create client and execute query
    client = PrometheusClient(url=url, auth=auth)
    try:
        result = client.query(clean_query, time_range)
    except requests.RequestException as e:
        # Handle errors
        error_message = f"Error querying Prometheus: {str(e)}"
        if output:
            return Html(f'<div class="promql-error">{error_message}</div>')
        raise RuntimeError(error_message) from e
    
    # Convert result to DataFrame
    df = _convert_prometheus_result_to_df(result.get("data", {}))
    
    # Display visualization if output is enabled
    if output and not df.empty:
        description = metadata.get("description", "PromQL Query Results")
        
        # Create visualization
        import altair as alt
        
        # For time series data
        if "time" in df.columns and "value" in df.columns and "metric" in df.columns:
            chart = alt.Chart(df).mark_line().encode(
                x=alt.X("time:T", title="Time"),
                y=alt.Y("value:Q", title="Value"),
                color=alt.Color("metric:N", title="Metric")
            ).properties(
                title=description,
                width="container",
                height=300
            ).interactive()
            
            # Create a display with both the chart and the table
            result_container = mo.ui.tabs({
                "Chart": mo.md(f"### {description}").append(mo.ui.altair_chart(chart)),
                "Table": mo.ui.dataframe(df)
            })
            mo.output.append(result_container)
    
    return df