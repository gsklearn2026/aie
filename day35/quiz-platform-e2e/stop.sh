#!/bin/bash

# Stop script for E2E Testing Environment
echo "🛑 Stopping E2E Testing Environment"

# Stop Docker services
if [ -f "docker/docker-compose.e2e.yml" ]; then
    echo "Stopping Docker services..."
    cd docker
    docker-compose -f docker-compose.e2e.yml down
    cd ..
fi

# Stop local processes
if [ -f ".backend.pid" ]; then
    echo "Stopping backend..."
    kill $(cat .backend.pid) 2>/dev/null || true
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    echo "Stopping frontend..."
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

echo "✅ All services stopped!"
