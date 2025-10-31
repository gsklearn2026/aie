#!/bin/bash

echo "🛑 Stopping AI Quiz Platform services..."

# Stop backend
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    kill $BACKEND_PID 2>/dev/null
    rm .backend_pid
    echo "🖥️ Backend stopped"
fi

# Stop frontend
if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill $FRONTEND_PID 2>/dev/null
    rm .frontend_pid
    echo "🌐 Frontend stopped"
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

echo "✅ All services stopped"
