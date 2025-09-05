#!/bin/bash

echo "🛑 Stopping Quiz Platform API Versioning System"
echo "==============================================="

if [ "$1" = "2" ]; then
    echo "🐳 Stopping Docker containers..."
    docker-compose down
    echo "✅ Docker services stopped"
else
    echo "🐍 Stopping local services..."
    
    # Stop backend
    if [ -f backend.pid ]; then
        kill $(cat backend.pid) 2>/dev/null
        rm backend.pid
        echo "✅ Backend stopped"
    fi
    
    # Stop frontend
    if [ -f frontend.pid ]; then
        kill $(cat frontend.pid) 2>/dev/null
        rm frontend.pid
        echo "✅ Frontend stopped"
    fi
fi

echo "🏁 All services stopped"
