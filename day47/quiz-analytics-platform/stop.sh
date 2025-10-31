#!/bin/bash

echo "🛑 Stopping Quiz Analytics Platform"
echo "==================================="

if [ -f docker-compose.yml ] && docker-compose ps -q > /dev/null 2>&1; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
    echo "✅ Docker services stopped!"
else
    echo "💻 Stopping local services..."
    
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null
        rm .backend.pid
        echo "🔧 Backend stopped"
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        rm .frontend.pid
        echo "⚛️ Frontend stopped"
    fi
    
    echo "✅ Local services stopped!"
fi
