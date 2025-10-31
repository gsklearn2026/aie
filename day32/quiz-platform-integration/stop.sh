#!/bin/bash

echo "🛑 Stopping Quiz Platform Services"
echo "================================="

# Stop Docker services
if [ -f "docker/docker-compose.test.yml" ]; then
    cd docker
    docker-compose -f docker-compose.test.yml down
    cd ..
    echo "🐳 Docker services stopped"
fi

# Stop local processes
pkill -f "python main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

echo "✅ All services stopped"
