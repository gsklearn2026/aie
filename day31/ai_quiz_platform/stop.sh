#!/bin/bash

echo "=== AI Quiz Platform - Stopping Services ==="

# Kill any running test watchers
pkill -f "pytest-watch" 2>/dev/null || true
pkill -f "ptw" 2>/dev/null || true

# Kill any coverage dashboard servers
pkill -f "coverage_dashboard.py" 2>/dev/null || true

# Kill any Python HTTP servers on port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Deactivate virtual environment if active
if [ "$VIRTUAL_ENV" != "" ]; then
    deactivate 2>/dev/null || true
fi

echo "✓ All services stopped"
echo "✓ Virtual environment deactivated"
echo "✓ Test watchers terminated"
echo "✓ Coverage dashboard stopped"

# Clean up temporary files
rm -f coverage_dashboard.html 2>/dev/null || true
rm -f coverage_dashboard.py 2>/dev/null || true

echo "✓ Temporary files cleaned up"
echo ""
echo "🎯 Unit Testing Demo Stopped Successfully!"
