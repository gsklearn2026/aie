#!/bin/bash

set -e

echo "=========================================="
echo "Building Content Curation System"
echo "=========================================="

# Check for Docker or local mode
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    docker-compose build
    echo "Docker build complete!"
    echo ""
    echo "To start: docker-compose up"
else
    echo "Building locally..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend setup
    echo "Setting up frontend..."
    cd frontend
    npm install
    cd ..
    
    echo ""
    echo "Local build complete!"
    echo ""
    echo "To start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "To start frontend: cd frontend && npm start"
fi

# Run tests
echo ""
echo "Running tests..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python -m pytest tests/ -v
cd ..

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
