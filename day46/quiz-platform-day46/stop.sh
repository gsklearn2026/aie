#!/bin/bash

echo "🛑 Stopping Quiz Taking Interface System..."

# Stop Docker containers
if docker-compose ps | grep -q "Up"; then
    echo "🐳 Stopping Docker containers..."
    docker-compose down
fi

# Stop local processes
if [ -f .backend_pid ]; then
    echo "🐍 Stopping backend server..."
    kill $(cat .backend_pid) 2>/dev/null || true
    rm .backend_pid
fi

if [ -f .frontend_pid ]; then
    echo "⚛️ Stopping frontend server..."
    kill $(cat .frontend_pid) 2>/dev/null || true
    rm .frontend_pid
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

echo "✅ All services stopped!"
