#!/bin/bash

echo "Stopping Quiz API Optimization System..."

USE_DOCKER=false
if [ "$1" == "--docker" ]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    docker-compose down
else
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi
    
    pkill -f "uvicorn backend.api.main"
    pkill -f "react-scripts start"
fi

echo "✅ System stopped"
