#!/usr/bin/env python3

# Simple script to test if our modules are importable
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from marimo._observability import promql, logql, grafana_dashboard
    print("Successfully imported promql, logql, and grafana_dashboard modules!")
    
    # Print module paths
    print(f"promql module: {promql.__file__}")
    print(f"logql module: {logql.__file__}")
    print(f"grafana_dashboard module: {grafana_dashboard.__file__}")
except ImportError as e:
    print(f"Import error: {e}")

print("Test completed.")