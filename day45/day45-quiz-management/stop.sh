#!/bin/bash

echo "🛑 Stopping Quiz Management Platform"
echo "===================================="

USE_DOCKER=${1:-false}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Stopping Docker containers..."
    docker-compose down
else
    echo "🔨 Stopping local processes..."
    
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm .backend.pid
        echo "Backend stopped"
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm .frontend.pid
        echo "Frontend stopped"
    fi
fi

echo "✅ Application stopped"
