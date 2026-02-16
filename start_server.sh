#!/bin/bash

echo "======================================================================"
echo "PR Test Scenario Generator - Web Application"
echo "======================================================================"
echo ""
echo "Starting server..."
echo ""
echo "Once started, open your browser and go to:"
echo "http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================================"
echo ""

cd "$(dirname "$0")"
source venv/Scripts/activate
python app.py
