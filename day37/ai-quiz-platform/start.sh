#!/bin/bash

set -e

echo "🚀 AI Quiz Platform - Start Script"
echo "================================="

# Function to show menu
show_menu() {
    echo ""
    echo "Choose start option:"
    echo "1) Start with Docker"
    echo "2) Start without Docker (Local)"
    echo "3) Exit"
    read -p "Enter your choice (1-3): " choice
}

# Start with Docker
start_with_docker() {
    echo "🐳 Starting with Docker..."
    
    # Check if containers exist
    if [ ! "$(docker-compose ps -q)" ]; then
        echo "🔨 No containers found. Building first..."
        docker-compose up --build -d
    else
        echo "▶️  Starting existing containers..."
        docker-compose up -d
    fi
    
    # Wait for services
    echo "⏳ Waiting for services..."
    sleep 15
    
    # Show service status
    echo "📊 Service Status:"
    docker-compose ps
    
    # Show URLs
    echo ""
    echo "🌐 Application URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📋 Useful commands:"
    echo "View logs: docker-compose logs -f [service_name]"
    echo "Stop services: docker-compose down"
    echo "Restart service: docker-compose restart [service_name]"
}

# Start without Docker
start_without_docker() {
    echo "🏠 Starting without Docker..."
    
    # Check if environment is set up
    if [ ! -d "backend/venv" ]; then
        echo "❌ Backend not set up. Run ./build.sh first"
        exit 1
    fi
    
    # Start backend in background
    echo "🐍 Starting backend..."
    cd backend
    source venv/bin/activate
    export $(cat ../.env.local | xargs)
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend in background
    echo "⚛️  Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo ""
    echo "📝 Process IDs:"
    echo "Backend: $BACKEND_PID"
    echo "Frontend: $FRONTEND_PID"
    echo ""
    echo "🛑 To stop: kill $BACKEND_PID $FRONTEND_PID"
    
    # Wait for user input to stop
    read -p "Press Enter to stop services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "🛑 Services stopped"
}

# Main execution
show_menu

case $choice in
    1)
        start_with_docker
        ;;
    2)
        start_without_docker
        ;;
    3)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
