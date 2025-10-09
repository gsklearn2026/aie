#!/bin/bash
set -e

USE_DOCKER=${1:-"local"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Starting services with Docker..."
    docker-compose up -d
    
    echo "Services starting..."
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000" 
    echo "Database: localhost:5432"
    echo ""
    echo "To view logs: docker-compose logs -f"
    
else
    echo "💻 Starting services locally..."
    
    # Set virtual environment name
    VENV_NAME="venv"
    
    # Activate virtual environment
    source $VENV_NAME/bin/activate
    
    # Start background services
    echo "Starting backup service..."
    python -m src.backup_service.main &
    BACKUP_PID=$!
    
    echo "Starting recovery service..."
    python -m src.recovery_service.main &
    RECOVERY_PID=$!
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Save PIDs for stopping later
    echo $BACKUP_PID > .backup_pid
    echo $RECOVERY_PID > .recovery_pid
    echo $FRONTEND_PID > .frontend_pid
    
    echo ""
    echo "✅ Services started!"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo ""
    echo "To stop services: ./stop.sh"
fi
