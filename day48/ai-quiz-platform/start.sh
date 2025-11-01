#!/bin/bash

echo "🚀 Starting AI Quiz Platform"
echo "============================"

# Check if Docker should be used
USE_DOCKER=${1:-"no"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Starting with Docker..."
    docker-compose up
else
    echo "📦 Starting without Docker..."
    
    # Start backend
    echo "Starting backend server..."
    cd backend || exit 1
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    cd ..
    
    # Wait a moment for backend to start
    sleep 2
    
    # Start frontend
    echo "Starting frontend server..."
    cd frontend || exit 1
    if [ -f "package.json" ]; then
        npm start &
        FRONTEND_PID=$!
        echo "Frontend started with PID: $FRONTEND_PID"
    fi
    cd ..
    
    echo ""
    echo "✅ Services started!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for user interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
fi

