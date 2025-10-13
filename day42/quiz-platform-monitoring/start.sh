#!/bin/bash

echo "🚀 Starting Quiz Platform Monitoring Services"
echo "============================================="

# Function to check if running in Docker
check_docker() {
    if docker-compose ps >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Start with Docker
start_docker() {
    echo "🐳 Starting Docker services..."
    docker-compose up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check service health
    echo "🏥 Checking service health..."
    curl -s http://localhost:8000/health || echo "❌ Backend not ready"
    curl -s http://localhost:3000 || echo "❌ Frontend not ready"
    
    echo "✅ Services started successfully!"
    echo "🌐 Frontend Dashboard: http://localhost:3000"
    echo "📊 Backend API: http://localhost:8000"
    echo "📈 Prometheus: http://localhost:9090"
    echo "📊 Grafana: http://localhost:3001 (admin/admin)"
}

# Start natively
start_native() {
    echo "🖥️  Starting native services..."
    
    # Start backend
    echo "Starting Python backend..."
    cd backend
    source venv/bin/activate || source venv/Scripts/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    echo $! > ../backend.pid
    cd ..
    
    # Start frontend
    echo "Starting React frontend..."
    cd frontend
    nohup npm start > ../frontend.log 2>&1 &
    echo $! > ../frontend.pid
    cd ..
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    echo "✅ Services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "📊 Backend: http://localhost:8000"
}

# Main execution
if check_docker; then
    start_docker
else
    start_native
fi

echo ""
echo "📝 To stop services, run: ./stop.sh"
echo "📊 To view logs:"
if check_docker; then
    echo "   docker-compose logs -f"
else
    echo "   tail -f backend.log frontend.log"
fi
