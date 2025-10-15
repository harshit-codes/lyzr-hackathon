#!/bin/bash
"""
SuperSuite Streamlit App Launcher

This script launches the SuperSuite web application.
Make sure you have all dependencies installed before running.

Usage:
    ./run_supersuite.sh
    or
    streamlit run streamlit_app.py
"""

# Set environment variables for better performance
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the Streamlit app
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0