#!/bin/bash

set -e

echo "🚀 Starting Quiz Platform API Integration Layer"
echo "==============================================="

# Check for Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    DOCKER_AVAILABLE=true
else
    DOCKER_AVAILABLE=false
fi

echo ""
echo "Choose startup option:"
echo "1) Local development"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "2) Docker containers"
fi
echo ""

read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "🔧 Starting local development servers..."
        
        # Check if Redis is running
        if ! pgrep -x "redis-server" > /dev/null; then
            echo "🔴 Starting Redis..."
            if command -v redis-server &> /dev/null; then
                redis-server --daemonize yes
                sleep 2
            else
                echo "❌ Redis not found. Please install Redis or use Docker option."
                exit 1
            fi
        else
            echo "✅ Redis already running"
        fi
        
        # Start backend
        echo "🔴 Starting Python backend..."
        cd backend
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
        
        # Start backend in background
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        cd ..
        
        # Wait for backend to start
        echo "⏳ Waiting for backend to start..."
        sleep 5
        
        # Start frontend
        echo "🔴 Starting React frontend..."
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        echo ""
        echo "✅ Application started successfully!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔧 Backend API: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        echo ""
        echo "Press Ctrl+C to stop all services"
        
        # Function to cleanup processes
        cleanup() {
            echo ""
            echo "🛑 Stopping services..."
            kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
            echo "✅ All services stopped"
        }
        
        # Trap Ctrl+C
        trap cleanup SIGINT
        
        # Wait for processes
        wait
        ;;
        
    2)
        if [ "$DOCKER_AVAILABLE" = true ]; then
            echo "🐳 Starting Docker containers..."
            
            cd docker
            
            # Start services
            docker-compose up -d
            
            echo "⏳ Waiting for services to start..."
            sleep 10
            
            echo ""
            echo "✅ Application started successfully!"
            echo "🌐 Frontend: http://localhost:3000"
            echo "🔧 Backend API: http://localhost:8000"
            echo "📚 API Docs: http://localhost:8000/docs"
            echo ""
            echo "To stop: ./stop.sh"
            echo "To view logs: docker-compose -f docker/docker-compose.yml logs -f"
            
            cd ..
        else
            echo "❌ Docker not available"
            exit 1
        fi
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
