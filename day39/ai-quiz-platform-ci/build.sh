#!/bin/bash
# Build script for AI Quiz Platform with CI Pipeline

set -e

echo "🏗️  Building AI Quiz Platform..."

# Function to show options
show_options() {
    echo "Usage: ./build.sh [option]"
    echo "Options:"
    echo "  docker    - Build with Docker"
    echo "  local     - Build locally"
    echo "  test      - Run tests only"
    echo "  all       - Build, test, and demo"
}

# Docker build function
build_with_docker() {
    echo "📦 Building with Docker..."
    
    # Build backend
    echo "Building backend..."
    cd backend
    docker build -t quiz-backend:latest .
    cd ..
    
    # Build frontend
    echo "Building frontend..."
    cd frontend
    npm install
    npm run build
    docker build -t quiz-frontend:latest .
    cd ..
    
    echo "✅ Docker build completed"
}

# Local build function
build_locally() {
    echo "💻 Building locally..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        python -m venv venv
    fi
    
    source venv/bin/activate || source venv/Scripts/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend setup
    echo "Setting up frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    
    echo "✅ Local build completed"
}

# Test function
run_tests() {
    echo "🧪 Running tests..."
    
    # Backend tests
    echo "Running backend tests..."
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate || source venv/Scripts/activate
    fi
    pytest tests/ -v
    cd ..
    
    # Frontend tests
    echo "Running frontend tests..."
    cd frontend
    npm run test:ci
    cd ..
    
    echo "✅ Tests completed"
}

# Demo function
run_demo() {
    echo "🚀 Starting demo..."
    
    echo "Backend will be available at: http://localhost:8000"
    echo "Frontend will be available at: http://localhost:3000"
    echo "API docs will be available at: http://localhost:8000/docs"
    
    # Check if using Docker
    if command -v docker &> /dev/null && docker images | grep -q quiz-backend; then
        echo "Starting with Docker Compose..."
        docker-compose up -d
    else
        echo "Starting locally..."
        
        # Start backend
        cd backend
        if [ -d "venv" ]; then
            source venv/bin/activate || source venv/Scripts/activate
        fi
        uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        cd frontend
        npm start &
        FRONTEND_PID=$!
        cd ..
        
        echo "Backend PID: $BACKEND_PID"
        echo "Frontend PID: $FRONTEND_PID"
        
        # Store PIDs for cleanup
        echo "$BACKEND_PID" > .backend.pid
        echo "$FRONTEND_PID" > .frontend.pid
    fi
    
    echo "✅ Demo started successfully"
    echo "Press Ctrl+C to stop or run ./stop.sh"
}

# Main script logic
case "$1" in
    docker)
        build_with_docker
        ;;
    local)
        build_locally
        ;;
    test)
        run_tests
        ;;
    demo)
        run_demo
        ;;
    all)
        build_locally
        run_tests
        run_demo
        ;;
    *)
        show_options
        ;;
esac
