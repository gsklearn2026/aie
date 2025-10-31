#!/bin/bash

echo "🚀 Building Quiz Analytics Platform - Day 47"
echo "============================================="

# Check if running with Docker
if [ "$1" = "--docker" ]; then
    echo "🐳 Building with Docker..."
    
    # Build and start services
    docker-compose down -v
    docker-compose build
    docker-compose up -d postgres redis
    
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Start application services
    docker-compose up -d backend frontend
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Create sample data
    echo "🔧 Creating sample data..."
    docker-compose exec backend python app/utils/sample_data.py
    
    echo "✅ Docker build complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
    
else
    echo "💻 Building without Docker..."
    
    # Setup Python backend
    echo "🔧 Setting up Python backend..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Initialize database
    echo "🗃️ Initializing database..."
    python -c "
from app.database.connection import init_db
import asyncio
asyncio.run(init_db())
"
    
    # Create sample data
    echo "📊 Creating sample data..."
    python app/utils/sample_data.py
    
    # Setup React frontend
    echo "⚛️ Setting up React frontend..."
    cd ../frontend
    npm install
    npm run build
    
    cd ..
    
    echo "✅ Build complete!"
    echo "📋 Next steps:"
    echo "   1. Run: ./start.sh (to start all services)"
    echo "   2. Run: ./start.sh --docker (to start with Docker)"
fi

# Run tests
echo "🧪 Running tests..."
if [ "$1" = "--docker" ]; then
    docker-compose exec backend python -m pytest tests/ -v
    # Frontend tests would run here
else
    cd backend
    source venv/bin/activate
    python -m pytest tests/ -v
    cd ../frontend
    npm test -- --coverage --passWithNoTests --watchAll=false
    cd ..
fi

echo "🎉 Build and test completed successfully!"
