#!/bin/bash

echo "🚀 Starting Quiz Platform..."

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --docker    Start with Docker"
    echo "  --env ENV   Set environment (development|testing|production)"
    echo "  --help      Show this help message"
}

# Default values
USE_DOCKER=false
ENVIRONMENT="development"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

if [ "$USE_DOCKER" = true ]; then
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    echo "✅ Services started with Docker"
else
    echo "🏗️ Starting without Docker..."
    
    # Load environment variables
    if [ -f ".env.$ENVIRONMENT" ]; then
        source .env.$ENVIRONMENT
        echo "✅ Environment loaded: $ENVIRONMENT"
    fi
    
    # Start backend in background
    echo "🐍 Starting backend server..."
    source venv/bin/activate
    cd backend
    python -m src.main &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Start frontend in background
    echo "⚛️ Starting frontend server..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    cd ..
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend_pid
    echo $FRONTEND_PID > .frontend_pid
    
    echo "✅ All services started"
fi

echo ""
echo "🌐 Application URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Health:   http://localhost:8000/health"
echo ""
echo "🛑 To stop services, run: ./stop.sh"
