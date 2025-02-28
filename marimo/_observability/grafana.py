"""Grafana dashboard integration for Marimo.

This module provides functions for embedding Grafana dashboards in Marimo notebooks.
"""

import re
from typing import Any, Dict, Optional
import urllib.parse

from marimo._output.hypertext import Html


def _extract_metadata_from_comments(content: str) -> Dict[str, Any]:
    """Extract metadata from comments.
    
    Handles comments like:
    # @dashboard: my-dashboard
    # @from: -6h
    # @to: now
    # @var-instance: server1
    """
    metadata = {}
    
    # Match comments that have @key: value format
    pattern = r"#\s*@([a-zA-Z_-]+):\s*(.+)$"
    
    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            key, value = match.groups()
            metadata[key] = value.strip()
    
    return metadata


def grafana_dashboard(
    content: str = "",
    url: Optional[str] = None,
    dashboard: Optional[str] = None,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    theme: str = "light",
    variables: Dict[str, str] = {},
    height: str = "500px",
    width: str = "100%",
    refresh: str = "off"
) -> Html:
    """Embed a Grafana dashboard in a Marimo notebook.
    
    Args:
        content: Optional content with metadata comments
        url: Grafana URL (if None, uses environment variable GRAFANA_URL)
        dashboard: Dashboard UID or slug
        from_time: From time (relative like "now-6h" or absolute)
        to_time: To time (relative like "now" or absolute)
        theme: Dashboard theme ("light" or "dark")
        variables: Dictionary of dashboard variables
        height: Height of the embedded dashboard
        width: Width of the embedded dashboard
        refresh: Refresh interval ("off" or a duration like "5s", "1m", etc.)
    
    Returns:
        HTML component with embedded dashboard
    """
    import os
    
    # Extract metadata from content
    metadata = _extract_metadata_from_comments(content)
    
    # Get URL from params, metadata, or environment
    if url is None:
        url = metadata.get("url") or os.environ.get("GRAFANA_URL")
        if url is None:
            raise ValueError(
                "Grafana URL not provided. Either set the GRAFANA_URL "
                "environment variable, include a # @url: comment, or pass the url parameter."
            )
    
    # Remove trailing slash if present
    url = url.rstrip("/")
    
    # Get dashboard from params or metadata
    if dashboard is None:
        dashboard = metadata.get("dashboard")
        if dashboard is None:
            raise ValueError(
                "Dashboard ID not provided. Include a # @dashboard: comment "
                "or pass the dashboard parameter."
            )
    
    # Get time range from params or metadata
    if from_time is None:
        from_time = metadata.get("from", "now-6h")
    
    if to_time is None:
        to_time = metadata.get("to", "now")
    
    # Process variables from metadata
    # Look for variables in metadata (format: var-<name>: <value>)
    for key, value in metadata.items():
        if key.startswith("var-"):
            variables[key] = value
    
    # Build dashboard URL
    dashboard_url = f"{url}/d-solo/{dashboard}"
    
    # Add query parameters
    params = {
        "orgId": "1",
        "from": from_time,
        "to": to_time,
        "theme": theme,
        "refresh": refresh
    }
    
    # Add variables as query parameters
    for var_name, var_value in variables.items():
        params[var_name] = var_value
    
    # Construct full URL
    query_string = urllib.parse.urlencode(params)
    embed_url = f"{dashboard_url}?{query_string}"
    
    # Create iframe HTML
    iframe_html = f"""
    <div class="grafana-dashboard" style="width: {width}; height: {height}; margin: 0 auto;">
        <iframe 
            src="{embed_url}" 
            width="100%" 
            height="100%" 
            frameborder="0"
            style="border: 1px solid #d3d3d3; border-radius: 4px;"
        ></iframe>
    </div>
    """
    
    return Html(iframe_html)