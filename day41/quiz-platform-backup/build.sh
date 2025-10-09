#!/bin/bash
set -e

echo "🚀 Building Quiz Platform Backup & Recovery System"
echo "=================================================="

# Check if Docker is requested
USE_DOCKER=${1:-"local"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Building with Docker..."
    
    # Build Docker images
    docker-compose build
    
    # Start services
    echo "Starting services with Docker..."
    docker-compose up -d
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 30
    
    # Run tests
    echo "Running tests..."
    docker-compose exec backup_service python -m pytest tests/ -v
    
else
    echo "💻 Building locally..."
    
    # Define virtual environment name
    VENV_NAME="venv"
    
    # Create virtual environment
    if [ ! -d "$VENV_NAME" ]; then
        python3 -m venv $VENV_NAME
        echo "✅ Virtual environment created"
    fi
    
    # Activate virtual environment
    source $VENV_NAME/bin/activate
    
    # Install Python dependencies
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install frontend dependencies
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    # Run database setup
    echo "🗄️ Setting up databases..."
    # Note: In production, you would run actual database setup here
    
    # Build frontend
    echo "🏗️ Building frontend..."
    cd frontend
    npm run build
    cd ..
    
    # Run tests
    echo "🧪 Running tests..."
    python -m pytest tests/ -v
    
    echo "✅ Build completed successfully!"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Start services: ./start.sh"
echo "2. Access dashboard: http://localhost:3000"
echo "3. Access API: http://localhost:8000"
echo "4. Stop services: ./stop.sh"
