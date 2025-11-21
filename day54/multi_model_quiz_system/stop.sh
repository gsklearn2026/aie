#!/bin/bash

echo "Stopping Multi-Model Quiz Generation System..."

echo "Select stop option:"
echo "1) Stop local services"
echo "2) Stop Docker services"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "Stopping local services..."
    pkill -f "uvicorn app.main:app"
    pkill -f "react-scripts start"
    echo "Services stopped"
    
elif [ "$choice" = "2" ]; then
    echo "Stopping Docker services..."
    docker-compose down
    echo "Docker services stopped"
    
else
    echo "Invalid choice"
    exit 1
fi
