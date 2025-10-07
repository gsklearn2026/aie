#!/bin/bash

echo "🚀 Starting Quiz Platform CD Dashboard"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 is required but not installed."
    echo "   Please install Python3 to run the dashboard server."
    exit 1
fi

# Check if services are running
echo "🔍 Checking if Quiz Platform services are running..."
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Staging service (port 8001) is not responding"
    echo "   Run './start.sh' first to start the services"
fi

if ! curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Production service (port 8002) is not responding"
    echo "   Run './start.sh' first to start the services"
fi

echo ""
echo "🌐 Starting dashboard server..."
echo "   Dashboard will be available at: http://localhost:3000"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the dashboard server
python3 serve-dashboard.py
