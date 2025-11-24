#!/bin/bash

echo "=========================================="
echo "Quiz Platform Production - Build Script"
echo "=========================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found! Please install Docker first."
    exit 1
fi

echo "Choose build option:"
echo "1. Build with Docker"
echo "2. Build without Docker (local)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo "Building with Docker..."
    
    # Build and start all services
    docker-compose build
    docker-compose up -d
    
    # Wait for services
    echo "Waiting for services to be ready..."
    sleep 15
    
    # Run tests
    echo "Running tests..."
    docker-compose exec backend-blue pytest tests/ -v || true
    
    echo ""
    echo "Build complete!"
    echo "Access the application at: http://localhost"
    echo "Prometheus monitoring at: http://localhost:9090"
    echo ""
    echo "To run post-deployment verification:"
    echo "  bash scripts/health-checks/verify.sh"
    echo ""
    echo "To stop all services:"
    echo "  bash stop.sh"

elif [ "$choice" == "2" ]; then
    echo "Building without Docker (local development)..."
    
    # Backend setup
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Set environment variables
    export DATABASE_URL="postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db"
    export REDIS_URL="redis://localhost:6379"
    
    # Start backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ../frontend
    npm install
    npm start &
    FRONTEND_PID=$!
    
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "Services started!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Note: Make sure PostgreSQL and Redis are running locally"
    
    cd ..
fi
