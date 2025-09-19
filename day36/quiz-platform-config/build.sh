#!/bin/bash
set -e

echo "🏗️ Quiz Platform Configuration Build Script"
echo "==========================================="

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --docker    Build and run with Docker"
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

echo "Environment: $ENVIRONMENT"
echo "Docker mode: $USE_DOCKER"
echo ""

if [ "$USE_DOCKER" = true ]; then
    echo "🐳 Building with Docker..."
    
    # Load environment variables
    if [ -f ".env.$ENVIRONMENT" ]; then
        export $(grep -v '^#' .env.$ENVIRONMENT | xargs)
        echo "✅ Loaded .env.$ENVIRONMENT"
    fi
    
    # Build and start with docker-compose
    docker-compose down -v
    docker-compose build
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    echo "🔍 Checking service health..."
    curl -f http://localhost:8000/health || echo "❌ Backend health check failed"
    curl -f http://localhost:3000 || echo "❌ Frontend health check failed"
    
else
    echo "🏗️ Building without Docker..."
    
    # Setup Python virtual environment
    echo "🐍 Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install backend dependencies
    echo "📦 Installing backend dependencies..."
    pip install -r backend/requirements.txt
    
    # Load environment variables
    if [ -f ".env.$ENVIRONMENT" ]; then
        source .env.$ENVIRONMENT
        echo "✅ Loaded .env.$ENVIRONMENT"
    fi
    
    # Create database
    echo "🗄️ Setting up database..."
    cd backend
    python -m src.config.database
    cd ..
    
    # Install frontend dependencies
    echo "⚛️ Setting up frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..
    
    # Run tests
    echo "🧪 Running tests..."
    cd backend
    python -m pytest src/tests/ -v
    cd ..
    
    echo "✅ Build completed successfully!"
fi

echo ""
echo "🎉 Build process completed!"
echo "Next steps:"
echo "  - Run ./start.sh to start the application"
echo "  - Access frontend: http://localhost:3000"
echo "  - Access backend: http://localhost:8000"
echo "  - API docs: http://localhost:8000/docs"
