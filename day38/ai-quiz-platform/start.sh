#!/bin/bash

echo "🚀 Starting AI Quiz Platform"
echo "============================"

# Parse arguments
USE_DOCKER=true
if [[ "$1" == "--no-docker" ]]; then
    USE_DOCKER=false
fi

if [[ "$USE_DOCKER" == true ]]; then
    echo "🐳 Starting with Docker Compose..."
    
    # Start in production mode if specified
    if [[ "$2" == "--prod" ]]; then
        echo "🏭 Production mode enabled"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    else
        echo "🔧 Development mode enabled"
        docker-compose up -d
    fi
    
    echo "⏳ Waiting for services..."
    sleep 15
    
    echo "📊 Service Status:"
    docker-compose ps
    
    echo "🏥 Health Check:"
    curl -s http://localhost:8000/health | python -m json.tool
    
    echo ""
    echo "✅ All services started!"
    echo "🌐 Access the application at: http://localhost:3000"
    echo "🔧 API endpoints at: http://localhost:8000"
    
else
    echo "🏠 Starting local development servers..."
    
    # Start backend
    echo "🐍 Starting Python backend..."
    cd backend
    source venv/bin/activate
    python app.py &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    echo "⚛️  Starting React frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Development servers started!"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
fi
