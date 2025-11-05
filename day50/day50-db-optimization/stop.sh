#!/bin/bash

echo "=== Stopping Quiz Platform ==="

if [ -f "docker-compose.yml" ]; then
    echo "Stopping Docker containers..."
    docker-compose down
else
    echo "Stopping local services..."
    
    if [ -f ".backend.pid" ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app"
    pkill -f "react-scripts start"
fi

echo "✓ Application stopped"
