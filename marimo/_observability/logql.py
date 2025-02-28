"""LogQL integration for Marimo.

This module provides functions for executing LogQL queries against Loki
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


class LokiTimeRange(BaseModel):
    """Time range for LogQL queries."""
    
    start: Union[str, datetime]
    end: Union[str, datetime, None] = None
    limit: int = 100
    
    def to_loki_params(self) -> Dict[str, str]:
        """Convert time range to Loki API parameters."""
        params = {"limit": str(self.limit)}
        
        # Handle start time
        if isinstance(self.start, datetime):
            params["start"] = str(int(self.start.timestamp() * 1e9))
        elif self.start.startswith("-") and self.start.endswith(("s", "m", "h", "d", "w", "y")):
            # Relative time like -1h
            offset = self._parse_relative_time(self.start)
            params["start"] = str(int((datetime.now() - offset).timestamp() * 1e9))
        else:
            params["start"] = self.start
            
        # Handle end time
        if self.end is None:
            params["end"] = str(int(datetime.now().timestamp() * 1e9))
        elif isinstance(self.end, datetime):
            params["end"] = str(int(self.end.timestamp() * 1e9))
        else:
            params["end"] = self.end
            
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


class LokiClient:
    """Client for Loki API."""
    
    def __init__(self, url: str, timeout: int = 30, auth: Optional[Tuple[str, str]] = None):
        """Initialize Loki client.
        
        Args:
            url: Loki API URL
            timeout: Request timeout in seconds
            auth: Optional (username, password) tuple for basic auth
        """
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.auth = auth
        self.session = requests.Session()
        
    def query(self, query: str, time_range: LokiTimeRange) -> Dict[str, Any]:
        """Execute a LogQL query."""
        endpoint = f"{self.url}/loki/api/v1/query_range"
        
        params = time_range.to_loki_params()
        params["query"] = query
        
        response = self.session.get(
            endpoint,
            params=params,
            timeout=self.timeout,
            auth=self.auth
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_label_names(self) -> List[str]:
        """Get available label names."""
        endpoint = f"{self.url}/loki/api/v1/labels"
        
        response = self.session.get(
            endpoint,
            timeout=self.timeout,
            auth=self.auth
        )
        
        response.raise_for_status()
        return response.json().get("data", [])
    
    def get_label_values(self, label: str) -> List[str]:
        """Get values for a specific label."""
        endpoint = f"{self.url}/loki/api/v1/label/{label}/values"
        
        response = self.session.get(
            endpoint,
            timeout=self.timeout,
            auth=self.auth
        )
        
        response.raise_for_status()
        return response.json().get("data", [])


def _extract_metadata_from_comments(query: str) -> Dict[str, Any]:
    """Extract metadata from query comments.
    
    Handles comments like:
    # @start_time: -1h
    # @limit: 100
    # @description: Payment Service Errors
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


def _parse_json_log(log: str) -> Dict[str, Any]:
    """Try to parse a log line as JSON."""
    try:
        return json.loads(log)
    except (json.JSONDecodeError, TypeError):
        return {"message": log}


def _convert_loki_result_to_df(result: Dict[str, Any]) -> pd.DataFrame:
    """Convert Loki API result to pandas DataFrame."""
    data = result.get("data", {})
    result_type = data.get("resultType")
    
    if result_type == "streams":
        # Log streams
        streams = data.get("result", [])
        rows = []
        
        for stream in streams:
            labels = stream.get("stream", {})
            
            # Create a readable labels string
            labels_str = ", ".join([f'{k}="{v}"' for k, v in labels.items()])
            
            # Process each log entry
            for entry in stream.get("values", []):
                if len(entry) == 2:
                    timestamp_ns, log = entry
                    
                    # Convert timestamp from nanoseconds to datetime
                    timestamp = pd.to_datetime(int(timestamp_ns), unit="ns")
                    
                    # Parse log as JSON if possible
                    parsed_log = _parse_json_log(log)
                    
                    # Create a row for the dataframe
                    row = {
                        "timestamp": timestamp,
                        "labels": labels_str,
                        "raw_log": log
                    }
                    
                    # Add parsed fields
                    for key, value in parsed_log.items():
                        if isinstance(value, (str, int, float, bool)) or value is None:
                            row[f"log.{key}"] = value
                    
                    rows.append(row)
        
        if rows:
            return pd.DataFrame(rows)
        return pd.DataFrame()
    
    elif result_type == "matrix":
        # Time series data (metric queries)
        frames = []
        
        for series in data.get("result", []):
            metric = series.get("metric", {})
            
            # Create labels string
            labels_str = ", ".join([f'{k}="{v}"' for k, v in metric.items()])
            
            # Convert values to dataframe
            values = series.get("values", [])
            if values:
                times, values = zip(*values)
                df = pd.DataFrame({
                    "timestamp": pd.to_datetime(times, unit="s"),
                    "value": values,
                    "labels": labels_str
                })
                frames.append(df)
        
        if frames:
            return pd.concat(frames, ignore_index=True)
        return pd.DataFrame()
    
    return pd.DataFrame()


def logql(
    query: str,
    url: Optional[str] = None,
    auth: Optional[Tuple[str, str]] = None,
    time_range: Optional[LokiTimeRange] = None,
    output: bool = True,
    parse_json: bool = True
) -> pd.DataFrame:
    """Execute a LogQL query and return the results.
    
    Args:
        query: LogQL query string (may include metadata comments)
        url: Loki API URL (if None, uses environment variable LOKI_URL)
        auth: Optional (username, password) tuple for basic auth
        time_range: Optional time range for the query
        output: Whether to display results as a visualization
        parse_json: Whether to parse JSON logs
    
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
        url = metadata.get("url") or os.environ.get("LOKI_URL")
        if url is None:
            raise ValueError(
                "Loki URL not provided. Either set the LOKI_URL "
                "environment variable, include a # @url: comment, or pass the url parameter."
            )
    
    # Create time range if not provided
    if time_range is None:
        start_time = metadata.get("start_time", "-1h")
        end_time = metadata.get("end_time")
        limit = int(metadata.get("limit", 100))
        
        time_range = LokiTimeRange(
            start=start_time,
            end=end_time,
            limit=limit
        )
    
    # Create client and execute query
    client = LokiClient(url=url, auth=auth)
    try:
        result = client.query(clean_query, time_range)
    except requests.RequestException as e:
        # Handle errors
        error_message = f"Error querying Loki: {str(e)}"
        if output:
            return Html(f'<div class="logql-error">{error_message}</div>')
        raise RuntimeError(error_message) from e
    
    # Convert result to DataFrame
    df = _convert_loki_result_to_df(result)
    
    # Display visualization if output is enabled
    if output and not df.empty:
        description = metadata.get("description", "LogQL Query Results")
        
        if "timestamp" in df.columns and "raw_log" in df.columns:
            # Log stream data
            # Create log display with syntax highlighting
            log_entries = []
            
            for _, row in df.iterrows():
                timestamp = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                labels = row["labels"]
                log = row["raw_log"]
                
                try:
                    # Try to format as JSON
                    parsed = json.loads(log)
                    formatted_log = json.dumps(parsed, indent=2)
                    log_html = f"<pre class='log-json'>{formatted_log}</pre>"
                except (json.JSONDecodeError, TypeError):
                    # Display as plain text
                    log_html = f"<pre class='log-text'>{log}</pre>"
                
                log_entries.append(f"""
                <div class="log-entry">
                    <div class="log-metadata">
                        <span class="log-time">{timestamp}</span>
                        <span class="log-labels">{labels}</span>
                    </div>
                    <div class="log-content">
                        {log_html}
                    </div>
                </div>
                """)
            
            log_display = f"""
            <div class="logql-results">
                <h3>{description}</h3>
                <div class="logs-container">
                    {''.join(log_entries)}
                </div>
            </div>
            <style>
                .logql-results .logs-container {{
                    max-height: 500px;
                    overflow-y: auto;
                    border: 1px solid #e5e5e5;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                }}
                .logql-results .log-entry {{
                    border-bottom: 1px solid #e5e5e5;
                    padding: 8px;
                }}
                .logql-results .log-metadata {{
                    margin-bottom: 5px;
                    font-family: monospace;
                    display: flex;
                    justify-content: space-between;
                }}
                .logql-results .log-time {{
                    color: #6c757d;
                }}
                .logql-results .log-labels {{
                    color: #007bff;
                    font-size: 0.85em;
                }}
                .logql-results .log-content pre {{
                    margin: 0;
                    white-space: pre-wrap;
                    font-family: monospace;
                    font-size: 0.9em;
                }}
                .logql-results .log-json {{
                    color: #333;
                }}
                .logql-results .log-text {{
                    color: #555;
                }}
                .logql-error {{
                    color: #dc3545;
                    padding: 10px;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    background-color: #f8d7da;
                }}
            </style>
            """
            
            # Create frequency chart if we have enough data
            if len(df) > 5:
                # Resample by minute to show log frequency over time
                freq_df = df.set_index("timestamp")
                freq_df["count"] = 1
                freq_chart = freq_df["count"].resample("1min").count().reset_index()
                
                # Create chart with altair
                import altair as alt
                
                freq_viz = alt.Chart(freq_chart).mark_bar().encode(
                    x=alt.X("timestamp:T", title="Time"),
                    y=alt.Y("count:Q", title="Log Count")
                ).properties(
                    width="container",
                    height=150,
                    title="Log Frequency Over Time"
                ).interactive()
                
                # Create a tabs display with logs, chart and table
                result_container = mo.ui.tabs({
                    "Logs": Html(log_display),
                    "Frequency": mo.ui.altair_chart(freq_viz),
                    "Table": mo.ui.dataframe(df)
                })
            else:
                # Just logs and table if not enough data for frequency chart
                result_container = mo.ui.tabs({
                    "Logs": Html(log_display),
                    "Table": mo.ui.dataframe(df)
                })
                
            mo.output.append(result_container)
        
        elif "timestamp" in df.columns and "value" in df.columns:
            # Metric query results (from LogQL)
            import altair as alt
            
            chart = alt.Chart(df).mark_line().encode(
                x=alt.X("timestamp:T", title="Time"),
                y=alt.Y("value:Q", title="Value"),
                color=alt.Color("labels:N", title="Labels")
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