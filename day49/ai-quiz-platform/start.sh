#!/bin/bash

echo "🚀 Starting AI Quiz Platform Services"
echo "====================================="

# Check if Docker or local environment
if [ -f "docker-compose.yml" ] && command -v docker-compose &> /dev/null; then
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "✅ Services started successfully!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 Health Check: http://localhost:8000/api/health"
else
    echo "💻 Starting local environment..."
    
    # Start backend
    cd backend
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    python app/main.py &
    echo $! > ../.backend.pid
    cd ..
    
    # Start frontend
    cd frontend
    npm start &
    echo $! > ../.frontend.pid
    cd ..
    
    echo "✅ Services starting..."
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
fi
