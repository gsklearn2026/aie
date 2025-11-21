#!/bin/bash

echo "=========================================="
echo "Starting Content Curation System"
echo "=========================================="

if [ "$1" == "--docker" ]; then
    echo "Starting with Docker..."
    docker-compose up -d
    echo ""
    echo "Services starting..."
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Starting locally..."
    
    # Start backend
    echo "Starting backend..."
    cd backend
    source venv/bin/activate
    export GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend
    sleep 3
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "Services started!"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    
    # Save PIDs for stop script
    echo "$BACKEND_PID" > .backend.pid
    echo "$FRONTEND_PID" > .frontend.pid
    
    wait
fi
