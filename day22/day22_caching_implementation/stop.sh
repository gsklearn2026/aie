#!/bin/bash

echo "🛑 Stopping Day 22: Caching Implementation Demo"

# Kill background processes
if [ -f backend.pid ]; then
    echo "Stopping backend..."
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    echo "Stopping frontend..."
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

# Stop Docker services
echo "Stopping Docker services..."
docker-compose down

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo "✅ All services stopped successfully!"
