#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=== Quiz Platform Production Build ==="
echo ""
echo "Choose build option:"
echo "1) Build with Docker"
echo "2) Build without Docker (local)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo "Building with Docker..."
        
        # Build backend Docker image
        echo "Building backend..."
        cd "$PROJECT_ROOT/backend"
        docker build -t quiz-backend:latest .
        cd "$PROJECT_ROOT"
        
        # Build frontend
        echo "Building frontend..."
        cd "$PROJECT_ROOT/frontend"
        npm install
        REACT_APP_ENV=production npm run build
        cd "$PROJECT_ROOT"
        
        # Build and start services
        echo "Starting services with Docker Compose..."
        docker-compose up -d
        
        echo "Waiting for services to be healthy..."
        sleep 30
        
        echo ""
        echo "=== Build Complete ==="
        echo "Services running:"
        docker-compose ps
        echo ""
        echo "Access points:"
        echo "- Frontend: http://localhost:80"
        echo "- API: http://localhost:80/api/"
        echo "- Health: http://localhost:80/health"
        echo "- Prometheus: http://localhost:9090"
        ;;
        
    2)
        echo "Building without Docker (local)..."
        
        # Setup backend
        echo "Setting up backend..."
        cd "$PROJECT_ROOT/backend"
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Copy development environment
        cp "$PROJECT_ROOT/configs/environments/.env.development" .env
        
        echo "Backend setup complete"
        cd "$PROJECT_ROOT"
        
        # Setup frontend
        echo "Setting up frontend..."
        cd "$PROJECT_ROOT/frontend"
        npm install
        echo "REACT_APP_ENV=development" > .env
        npm run build
        cd "$PROJECT_ROOT"
        
        echo ""
        echo "=== Build Complete (Local) ==="
        echo "To start services:"
        echo "1. Start PostgreSQL and Redis locally"
        echo "2. Run: $PROJECT_ROOT/start.sh"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
