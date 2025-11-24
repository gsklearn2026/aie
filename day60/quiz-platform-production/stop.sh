#!/bin/bash

echo "Stopping Quiz Platform..."

if command -v docker-compose &> /dev/null; then
    docker-compose down
    echo "Docker services stopped"
else
    pkill -f "uvicorn app.main:app"
    pkill -f "npm start"
    echo "Local services stopped"
fi
