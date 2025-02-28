#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A minimal test that only imports our new modules directly,
without depending on other marimo modules.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

print("Testing direct imports of our modules...")

try:
    # Import the modules directly without going through the marimo package
    sys.path.insert(0, str(project_dir / "marimo" / "_observability"))
    
    # First test if we can import the modules directly
    print("Trying to import promql.py...")
    import promql
    print("Successfully imported promql.py")
    
    print("Trying to import logql.py...")
    import logql
    print("Successfully imported logql.py")
    
    print("Trying to import grafana.py...")
    import grafana
    print("Successfully imported grafana.py")
    
    # Check the required imports
    print("\nChecking imports needed by our modules:")
    print("- requests:", "requests" in sys.modules)
    print("- pandas:", "pandas" in sys.modules)
    print("- pydantic:", "pydantic" in sys.modules)
    
    # Check if our module has any syntax errors
    print("\nModule attributes:")
    print("- promql has:", dir(promql)[:5], "...")
    print("- logql has:", dir(logql)[:5], "...")
    print("- grafana has:", dir(grafana)[:5], "...")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest completed.")

from marimo._observability import promql, logql, grafana_dashboard

print("Successfully imported observability modules")

# Try to use the promql function
try:
    result = promql(
        """
        # @description: Test Query
        # @start_time: -1h
        # @step: 15s
        
        avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100
        """,
        url="http://localhost:9090",
        output=False  # Don't output HTML
    )
    print("PromQL query executed successfully")
except Exception as e:
    print(f"Error executing PromQL query: {e}")

# Try to use the logql function
try:
    logs = logql(
        """
        # @description: Test Logs
        # @start_time: -1h
        # @limit: 100
        
        {app="test"} |= "error"
        """,
        url="http://localhost:3100",
        output=False  # Don't output HTML
    )
    print("LogQL query executed successfully")
except Exception as e:
    print(f"Error executing LogQL query: {e}")

# Try to use the grafana_dashboard function
try:
    dashboard = grafana_dashboard(
        """
        # @dashboard: test-dashboard
        # @from: now-6h
        # @to: now
        """,
        url="http://localhost:3000"
    )
    print("Grafana dashboard loaded successfully")
except Exception as e:
    print(f"Error loading Grafana dashboard: {e}")

print("Test completed")