#!/bin/bash
echo "========================================"
echo "AI Study Coach - Frontend"
echo "========================================"
echo ""
echo "Starting Streamlit application..."
echo "Make sure the backend server is running on port 8000"
echo ""
cd "$(dirname "$0")"
streamlit run app.py
