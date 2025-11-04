#!/bin/bash

echo "🛑 Stopping AI Quiz Platform Services"
echo "======================================"

# Check if Docker is running
if docker-compose ps | grep -q "Up"; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
else
    echo "💻 Stopping local services..."
    
    # Stop processes using saved PIDs
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null
        rm .backend.pid
        echo "Backend stopped"
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        rm .frontend.pid
        echo "Frontend stopped"
    fi
    
    # Fallback: kill by process name
    pkill -f "python app/main.py" 2>/dev/null
    pkill -f "npm start" 2>/dev/null
fi

echo "✅ All services stopped"
