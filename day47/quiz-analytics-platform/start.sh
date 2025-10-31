#!/bin/bash

echo "🚀 Starting Quiz Analytics Platform"
echo "=================================="

if [ "$1" = "--docker" ]; then
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    
    echo "⏳ Waiting for services..."
    sleep 10
    
    echo "✅ All services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📊 API Documentation: http://localhost:8000/docs"
    echo "📈 Postgres Admin: localhost:5432"
    
    # Show service status
    docker-compose ps
    
else
    echo "💻 Starting without Docker..."
    
    # Start backend
    echo "🔧 Starting backend..."
    cd backend
    source venv/bin/activate
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    echo "⚛️ Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📊 API Documentation: http://localhost:8000/docs"
    
    # Save PIDs for stop script
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
fi

echo "🎯 Demo completed! Analytics dashboard is ready."
echo "🔍 Check the dashboard for real-time analytics and insights."
