#!/bin/bash

echo "========================================="
echo "Starting Security Audit System"
echo "========================================="

if [ "$1" = "--docker" ]; then
    echo "Starting with Docker..."
    docker-compose up -d
    
    echo "Waiting for services..."
    sleep 5
    
    echo ""
    echo "✅ Services started!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
else
    echo "Starting without Docker..."
    
    # Start backend
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Services started!"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop"
    
    wait
fi
