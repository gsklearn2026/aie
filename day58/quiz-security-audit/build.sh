#!/bin/bash

echo "========================================="
echo "Building Security Audit System"
echo "========================================="

# Check for Docker option
if [ "$1" = "--docker" ]; then
    echo "Building with Docker..."
    docker-compose build
    docker-compose up -d
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo ""
    echo "✅ Services started successfully!"
    echo "Backend API: http://localhost:8000"
    echo "Frontend Dashboard: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Run './stop.sh' to stop all services"
else
    echo "Building without Docker..."
    
    # Backend
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend
    echo "Setting up frontend..."
    cd frontend
    npm install
    cd ..
    
    echo ""
    echo "✅ Build complete!"
    echo ""
    echo "To start services:"
    echo "1. Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "2. Frontend: cd frontend && npm start"
    echo ""
    echo "Or use './start.sh' to start both"
fi
