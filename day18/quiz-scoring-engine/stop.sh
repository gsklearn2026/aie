#!/bin/bash

echo "🛑 Stopping Quiz Scoring Engine Development Environment"

# Function to cleanup processes
cleanup() {
    echo "🛑 Stopping all services..."
    
    # Kill processes using PIDs if available
    if [ -f backend.pid ]; then
        echo "🛑 Stopping backend (PID: $(cat backend.pid))..."
        kill $(cat backend.pid) 2>/dev/null || true
        rm -f backend.pid
    fi
    
    if [ -f frontend.pid ]; then
        echo "🛑 Stopping frontend (PID: $(cat frontend.pid))..."
        kill $(cat frontend.pid) 2>/dev/null || true
        rm -f frontend.pid
    fi
    
    # Kill processes by name as backup
    echo "🛑 Stopping uvicorn processes..."
    pkill -f uvicorn 2>/dev/null || true
    
    echo "🛑 Stopping npm/react-scripts processes..."
    pkill -f "npm start" 2>/dev/null || true
    pkill -f "react-scripts" 2>/dev/null || true
    
    echo "🛑 Stopping Redis..."
    pkill -f redis-server 2>/dev/null || true
    
    # Remove log files
    rm -f frontend.log
    
    rm -rf venv
    rm -rf backend/venv
    rm -rf frontend/node_modules
    
    echo "✅ All services stopped"
}

# Run cleanup
cleanup

# Verify no processes are running
echo "🔍 Verifying all services are stopped..."
if pgrep -f "uvicorn|npm start|react-scripts|redis-server" >/dev/null; then
    echo "⚠️  Some processes might still be running. You can manually kill them:"
    pgrep -f "uvicorn|npm start|react-scripts|redis-server"
else
    echo "✅ All services successfully stopped"
fi
