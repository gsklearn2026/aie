#!/bin/bash

echo "🛑 Stopping Quiz Platform Monitoring Services"
echo "============================================="

# Stop Docker services
if docker-compose ps >/dev/null 2>&1; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
    echo "✅ Docker services stopped!"
else
    echo "🖥️  Stopping native services..."
    
    # Stop backend
    if [ -f backend.pid ]; then
        echo "Stopping backend..."
        kill $(cat backend.pid) 2>/dev/null || true
        rm -f backend.pid
    fi
    
    # Stop frontend
    if [ -f frontend.pid ]; then
        echo "Stopping frontend..."
        kill $(cat frontend.pid) 2>/dev/null || true
        rm -f frontend.pid
    fi
    
    # Clean up any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    
    echo "✅ Native services stopped!"
fi

echo "🧹 Cleaned up successfully!"
