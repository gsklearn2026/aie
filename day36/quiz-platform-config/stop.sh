#!/bin/bash

echo "🛑 Stopping Quiz Platform..."

if [ -f "docker-compose.yml" ] && docker-compose ps | grep -q "Up"; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
    echo "✅ Docker services stopped"
else
    echo "🏗️ Stopping local services..."
    
    # Kill backend process
    if [ -f ".backend_pid" ]; then
        BACKEND_PID=$(cat .backend_pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "✅ Backend stopped (PID: $BACKEND_PID)"
        fi
        rm .backend_pid
    fi
    
    # Kill frontend process
    if [ -f ".frontend_pid" ]; then
        FRONTEND_PID=$(cat .frontend_pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
        fi
        rm .frontend_pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
fi

echo "🏁 All services stopped"
