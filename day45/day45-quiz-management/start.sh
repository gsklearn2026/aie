#!/bin/bash

echo "🚀 Starting Quiz Management Platform"
echo "===================================="

USE_DOCKER=${1:-false}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    
    echo "✅ Application started!"
    echo "Frontend: http://localhost:5173"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    
else
    echo "🔨 Starting locally..."
    
    # Start backend
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Start frontend
    echo "Starting frontend server..."
    cd ../frontend
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # Save PIDs for stop script
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo "✅ Application started!"
    echo "Frontend: http://localhost:5173"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C or run ./stop.sh to stop"
    
    # Wait for processes
    wait $BACKEND_PID $FRONTEND_PID
fi
