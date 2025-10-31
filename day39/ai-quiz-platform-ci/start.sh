#!/bin/bash
# Start script for AI Quiz Platform

set -e

echo "🚀 Starting AI Quiz Platform..."

# Function to show options
show_options() {
    echo "Usage: ./start.sh [option]"
    echo "Options:"
    echo "  docker    - Start with Docker Compose"
    echo "  local     - Start locally"
}

start_with_docker() {
    echo "📦 Starting with Docker Compose..."
    
    # Check if images exist
    if ! docker images | grep -q quiz-backend; then
        echo "Building Docker images first..."
        ./build.sh docker
    fi
    
    docker-compose up -d
    
    echo "✅ Started with Docker"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "Logs: docker-compose logs -f"
}

start_locally() {
    echo "💻 Starting locally..."
    
    # Start backend
    cd backend
    if [ ! -d "venv" ]; then
        echo "Virtual environment not found. Run ./build.sh local first."
        exit 1
    fi
    
    source venv/bin/activate || source venv/Scripts/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    cd ..
    
    # Start frontend
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Node modules not found. Run ./build.sh local first."
        exit 1
    fi
    
    npm start &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    cd ..
    
    # Store PIDs
    echo "$BACKEND_PID" > .backend.pid
    echo "$FRONTEND_PID" > .frontend.pid
    
    echo "✅ Started locally"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
}

case "$1" in
    docker)
        start_with_docker
        ;;
    local)
        start_locally
        ;;
    *)
        show_options
        ;;
esac
