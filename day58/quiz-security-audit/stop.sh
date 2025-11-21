#!/bin/bash

echo "Stopping Security Audit System..."

if docker-compose ps | grep -q "Up"; then
    docker-compose down
    echo "✅ Docker services stopped"
else
    pkill -f "uvicorn app.main:app"
    pkill -f "react-scripts start"
    echo "✅ Services stopped"
fi
