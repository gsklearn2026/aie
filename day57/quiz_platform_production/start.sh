#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=== Starting Quiz Platform ==="
echo ""

# Accept choice as command-line argument, or prompt interactively
if [ -n "$1" ]; then
    choice="$1"
    echo "Using command-line option: $choice"
else
    echo "Choose startup option:"
    echo "1) Start with Docker"
    echo "2) Start without Docker (local)"
    echo ""
    read -p "Enter choice [1-2]: " choice
fi

case $choice in
    1)
        echo "Starting with Docker Compose..."
        cd "$PROJECT_ROOT"
        docker-compose up -d
        
        echo "Waiting for services..."
        sleep 20
        
        echo ""
        echo "=== Services Started ==="
        docker-compose ps
        echo ""
        echo "Access points:"
        echo "- Frontend: http://localhost:80"
        echo "- API Health: http://localhost:80/health"
        echo "- Metrics: http://localhost:9090"
        
        echo ""
        echo "View logs:"
        echo "  docker-compose logs -f"
        ;;
        
    2)
        echo "Starting services locally..."
        
        # Check if backend venv exists
        if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
            echo "Error: Backend virtual environment not found. Please run build.sh first."
            exit 1
        fi
        
        # Check if frontend node_modules exists
        if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
            echo "Error: Frontend node_modules not found. Please run build.sh first."
            exit 1
        fi
        
        # Start backend
        echo "Starting backend..."
        cd "$PROJECT_ROOT/backend"
        source venv/bin/activate
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        cd "$PROJECT_ROOT"
        
        # Start frontend
        echo "Starting frontend..."
        cd "$PROJECT_ROOT/frontend"
        REACT_APP_ENV=development npm start &
        FRONTEND_PID=$!
        cd "$PROJECT_ROOT"
        
        echo ""
        echo "=== Services Started (Local) ==="
        echo "Backend PID: $BACKEND_PID"
        echo "Frontend PID: $FRONTEND_PID"
        echo ""
        echo "Access points:"
        echo "- Frontend: http://localhost:3000"
        echo "- API: http://localhost:8000"
        echo "- Health: http://localhost:8000/health"
        
        echo ""
        echo "To stop services: $PROJECT_ROOT/stop.sh"
        
        # Save PIDs
        echo $BACKEND_PID > "$PROJECT_ROOT/.backend.pid"
        echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend.pid"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
