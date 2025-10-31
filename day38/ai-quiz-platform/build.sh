#!/bin/bash

echo "🚀 Building AI Quiz Platform - Day 38: Docker Compose"
echo "================================================="

# Parse command line arguments
USE_DOCKER=true
if [[ "$1" == "--no-docker" ]]; then
    USE_DOCKER=false
    echo "📝 Building without Docker (local development)"
else
    echo "🐳 Building with Docker Compose"
fi

if [[ "$USE_DOCKER" == true ]]; then
    # Docker Compose Build
    echo "🏗️  Building Docker images..."
    docker-compose build --no-cache
    
    echo "📋 Creating and starting services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    echo "🏥 Checking service health..."
    docker-compose exec backend curl -f http://localhost:8000/health || echo "Backend health check failed"
    
    echo "🧪 Running integration tests..."
    docker-compose exec backend python -c "
import requests
import json

# Test health endpoint
try:
    response = requests.get('http://localhost:8000/health')
    print(f'Health check: {response.status_code} - {response.json()}')
except Exception as e:
    print(f'Health check failed: {e}')

# Test quiz API
try:
    response = requests.get('http://localhost:8000/api/quizzes')
    print(f'Quizzes API: {response.status_code} - {len(response.json())} quizzes')
except Exception as e:
    print(f'Quizzes API failed: {e}')
"
    
    echo "✅ Docker Compose build completed!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo "📊 Nginx Proxy: http://localhost:80"
    
else
    # Local Development Build
    echo "🏠 Setting up local development environment..."
    
    # Backend setup
    echo "🐍 Setting up Python backend..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements/base.txt
    
    # Set environment variables
    export FLASK_APP=app.py
    export FLASK_ENV=development
    export DATABASE_URL=postgresql://quiz_admin:secure_quiz_2025@localhost:5432/quiz_platform
    export REDIS_URL=redis://localhost:6379/0
    
    cd ..
    
    # Frontend setup  
    echo "⚛️  Setting up React frontend..."
    cd frontend
    npm install
    cd ..
    
    echo "✅ Local development setup completed!"
    echo "📝 Start backend: cd backend && source venv/bin/activate && python app.py"
    echo "📝 Start frontend: cd frontend && npm start"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Check health endpoint: curl http://localhost:8000/health"
echo "2. Open browser to http://localhost:3000"
echo "3. Test quiz functionality"
echo "4. View Docker containers: docker-compose ps"
