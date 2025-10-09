#!/bin/bash

USE_DOCKER=${1:-"local"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
    
else
    echo "💻 Stopping local services..."
    
    # Kill background processes
    if [ -f .backup_pid ]; then
        kill $(cat .backup_pid) 2>/dev/null || true
        rm .backup_pid
    fi
    
    if [ -f .recovery_pid ]; then
        kill $(cat .recovery_pid) 2>/dev/null || true
        rm .recovery_pid
    fi
    
    if [ -f .frontend_pid ]; then
        kill $(cat .frontend_pid) 2>/dev/null || true
        rm .frontend_pid
    fi
    
    # Kill any remaining processes
    pkill -f "backup_service" || true
    pkill -f "recovery_service" || true
    pkill -f "react-scripts" || true
fi

echo "✅ Services stopped"
