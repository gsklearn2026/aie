#!/bin/bash

echo "🛑 Stopping Quiz Platform API Documentation System..."

# Kill Flask and React processes
pkill -f "python app.py"
pkill -f "react-scripts start"
pkill -f "npm start"

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo "✅ All services stopped successfully!"
