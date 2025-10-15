#!/bin/bash

echo "🛑 Stopping Quiz Platform services..."

# Stop Docker containers if running
if command -v docker-compose &> /dev/null; then
    if [ -f "docker/docker-compose.yml" ]; then
        cd docker
        docker-compose down
        cd ..
        echo "✅ Docker containers stopped"
    fi
fi

# Stop local processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "✅ All services stopped"
