#!/bin/bash

echo "=============================================="
echo "Day 56: Content Refresh - Stopping Services"
echo "=============================================="

USE_DOCKER=false
if [[ "$1" == "--docker" ]]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Stopping Docker services..."
    docker-compose down
    echo "Docker services stopped"
    
else
    echo "Stopping local services..."
    
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
        echo "Backend stopped"
    fi
    
    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
        echo "Frontend stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo "All services stopped"
fi
