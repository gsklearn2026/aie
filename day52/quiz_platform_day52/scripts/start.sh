#!/bin/bash

echo "🚀 Starting Quiz Platform - Day 52"

# Check if docker-compose.yml exists
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    echo "✅ Services started with Docker"
else
    echo "💻 Starting locally..."
    
    # Start backend
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    cd frontend
    BROWSER=none npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started locally"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    
    # Save PIDs
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
fi

echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Run './scripts/stop.sh' to stop the application"
