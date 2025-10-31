#!/bin/bash
# Stop script for AI Quiz Platform

echo "🛑 Stopping AI Quiz Platform..."

# Stop Docker if running
if docker-compose ps | grep -q Up; then
    echo "Stopping Docker Compose..."
    docker-compose down
fi

# Stop local processes
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID"
    fi
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID"
    fi
    rm .frontend.pid
fi

echo "✅ Stopped all services"
