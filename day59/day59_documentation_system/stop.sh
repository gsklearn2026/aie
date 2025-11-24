#!/bin/bash

echo "Stopping Documentation System..."

# Check if Docker is running
if docker-compose ps | grep -q "Up"; then
    echo "Stopping Docker containers..."
    docker-compose down
else
    echo "Stopping local processes..."
    pkill -f "uvicorn app.main:app"
    pkill -f "react-scripts start"
fi

echo "✓ All services stopped"
