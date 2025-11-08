#!/bin/bash

echo "🛑 Stopping Quiz Platform..."

if [ -f "docker-compose.yml" ] && [ "$(docker-compose ps -q)" ]; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
else
    echo "💻 Stopping local services..."
    
    if [ -f ".backend.pid" ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi
    
    # Cleanup any remaining processes
    pkill -f "uvicorn app.main:app"
    pkill -f "react-scripts start"
fi

echo "✅ All services stopped"
