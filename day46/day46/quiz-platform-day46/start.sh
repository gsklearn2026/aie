#!/bin/bash

echo "🚀 Starting Quiz Taking Interface System..."

# Function to choose start method
choose_start_method() {
    echo "Choose start method:"
    echo "1) Docker"
    echo "2) Local Development"
    read -p "Enter choice (1-2): " choice
    
    case $choice in
        1) start_docker ;;
        2) start_local ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
}

start_docker() {
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    
    echo "⏳ Waiting for services..."
    sleep 10
    
    echo "✅ System started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
}

start_local() {
    echo "💻 Starting locally..."
    
    # Start backend
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    echo $! > ../.backend_pid
    cd ..
    
    # Start frontend
    cd frontend
    npm start &
    echo $! > ../.frontend_pid
    cd ..
    
    echo "⏳ Waiting for services..."
    sleep 8
    
    echo "✅ System started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
}

case "${1:-choose}" in
    "choose") choose_start_method ;;
    "docker") start_docker ;;
    "local") start_local ;;
    *) 
        echo "Usage: $0 [choose|docker|local]"
        ;;
esac
