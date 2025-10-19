#!/bin/bash

echo "🚀 Starting AI Quiz Platform Authentication System..."

# Function to show usage
show_usage() {
    echo "Usage: $0 [--docker|--local]"
    echo "  --docker: Start with Docker"
    echo "  --local: Start locally"
    exit 1
}

# Parse arguments
START_MODE="local"
if [ "$1" = "--docker" ]; then
    START_MODE="docker"
elif [ "$1" = "--local" ] || [ -z "$1" ]; then
    START_MODE="local"
else
    show_usage
fi

if [ "$START_MODE" = "docker" ]; then
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    echo "✅ Services started with Docker!"
else
    echo "🏠 Starting locally..."
    
    # Start backend
    cd backend
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID)"
    
    # Start frontend
    cd ../frontend
    npm start &
    FRONTEND_PID=$!
    echo "Frontend started (PID: $FRONTEND_PID)"
    
    # Save PIDs
    echo $BACKEND_PID > ../backend.pid
    echo $FRONTEND_PID > ../frontend.pid
    
    echo "✅ Services started locally!"
fi

echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
