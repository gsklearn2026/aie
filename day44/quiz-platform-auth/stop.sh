#!/bin/bash

echo "🛑 Stopping AI Quiz Platform Authentication System..."

# Check if running with Docker
if [ -f "docker-compose.yml" ] && docker-compose ps | grep -q "Up"; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
    echo "✅ Docker services stopped!"
else
    echo "🏠 Stopping local services..."
    
    # Stop backend
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "Backend stopped (PID: $BACKEND_PID)"
        fi
        rm backend.pid
    fi
    
    # Stop frontend
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo "Frontend stopped (PID: $FRONTEND_PID)"
        fi
        rm frontend.pid
    fi
    
    echo "✅ Local services stopped!"
fi
