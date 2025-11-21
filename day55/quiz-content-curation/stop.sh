#!/bin/bash

echo "Stopping Content Curation System..."

if [ "$1" == "--docker" ]; then
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
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "react-scripts start" 2>/dev/null
fi

echo "Services stopped."
