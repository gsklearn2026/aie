#!/bin/bash

set -e

echo "🚀 Starting Quiz Platform Services"
echo "================================="

# Function to show options
show_options() {
    echo ""
    echo "Start Options:"
    echo "1. Start locally (without Docker)"
    echo "2. Start with Docker"
    echo "3. Start with demo data"
    echo ""
    read -p "Select option (1-3): " choice
    echo ""
}

# Local start function
start_local() {
    echo "🔄 Starting services locally..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Run './build.sh' first."
        exit 1
    fi
    
    # Start PostgreSQL and Redis (assuming they're running)
    echo "🗄️  Ensure PostgreSQL is running on port 5432"
    echo "🔴 Ensure Redis is running on port 6379"
    
    # Start API server
    source venv/bin/activate
    cd backend/src
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost/quizdb"
    python main.py &
    
    echo "✅ API server started on http://localhost:8000"
    echo "📋 API docs: http://localhost:8000/docs"
    
    # Wait for server to start
    sleep 3
    
    # Test health endpoint
    curl -f http://localhost:8000/health || echo "⚠️  API health check failed"
}

# Docker start function
start_docker() {
    echo "🐳 Starting with Docker..."
    
    cd docker
    docker-compose -f docker-compose.test.yml up -d
    cd ..
    
    echo "✅ Docker services started"
    echo "📋 API docs: http://localhost:8001/docs"
    
    # Wait for services
    sleep 10
    
    # Test health endpoint
    curl -f http://localhost:8001/health || echo "⚠️  API health check failed"
}

# Start with demo data
start_with_demo() {
    echo "🎭 Starting with demo data..."
    
    # Start services first
    start_local
    
    # Wait for API to be ready
    sleep 5
    
    # Create demo user
    echo "👤 Creating demo user..."
    curl -X POST "http://localhost:8000/api/auth/register" \
         -H "Content-Type: application/json" \
         -d '{"username": "demo_user", "email": "demo@example.com", "password": "demo123"}'
    
    echo ""
    
    # Create demo quiz
    echo "📝 Creating demo quiz..."
    QUIZ_RESPONSE=$(curl -X POST "http://localhost:8000/api/quiz/" \
                         -H "Content-Type: application/json" \
                         -d '{"title": "Demo Quiz", "description": "A demonstration quiz", "creator_id": 1}')
    
    QUIZ_ID=$(echo $QUIZ_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    
    echo ""
    echo "🧠 Generating demo questions..."
    curl -X POST "http://localhost:8000/api/quiz/$QUIZ_ID/questions" \
         -H "Content-Type: application/json" \
         -d '{"topic": "general knowledge", "count": 3}'
    
    echo ""
    echo "✅ Demo data created!"
    echo "🎯 Try: curl http://localhost:8000/api/quiz/$QUIZ_ID"
}

# Main execution
show_options

case $choice in
    1)
        start_local
        ;;
    2)
        start_docker
        ;;
    3)
        start_with_demo
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Services started successfully!"
echo "🔍 Monitor logs: docker logs quiz-platform-api (if using Docker)"
