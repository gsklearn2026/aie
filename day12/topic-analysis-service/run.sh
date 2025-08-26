#!/bin/bash
set -e

echo "🚀 Starting Topic Analysis Service"
echo "=================================="

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️ Redis not running. Starting Redis..."
    redis-server --daemonize yes
fi

# Start the application
echo "Starting Topic Analysis Service..."
cd src && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Service started at http://localhost:8000"
