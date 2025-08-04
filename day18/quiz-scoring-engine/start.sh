#!/bin/bash

echo "🚀 Starting Quiz Scoring Engine Development Environment"

# Function to cleanup processes
cleanup() {
    echo "🛑 Stopping all services..."
    if [ -f backend.pid ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm -f backend.pid
    fi
    if [ -f frontend.pid ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm -f frontend.pid
    fi
    pkill -f uvicorn 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    pkill -f redis-server 2>/dev/null || true
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Check if ports are already in use
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use by $service"
        echo "🛑 Stopping existing $service..."
        if [ "$service" = "frontend" ]; then
            pkill -f "npm start" 2>/dev/null || true
            pkill -f "react-scripts" 2>/dev/null || true
        elif [ "$service" = "backend" ]; then
            pkill -f uvicorn 2>/dev/null || true
        elif [ "$service" = "redis" ]; then
            pkill -f redis-server 2>/dev/null || true
        fi
        sleep 2
    fi
}

# Check ports before starting
echo "🔍 Checking port availability..."
check_port 8000 "backend"
check_port 3000 "frontend"
check_port 6379 "redis"

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip and setuptools first to fix build issues
echo "🔧 Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start Redis (if not running in Docker)
echo "🔴 Starting Redis..."
redis-server --daemonize yes --port 6379 || echo "Redis might already be running"

# Run backend tests
echo "🧪 Running backend tests..."
cd backend
python -m pytest tests/ -v
cd ..

# Run frontend tests
echo "🧪 Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

# Start backend
echo "🔧 Starting backend server..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Verify backend is running
if ! curl -s http://localhost:8000/health >/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi
echo "✅ Backend is running on http://localhost:8000"

# Start frontend
echo "🎨 Starting frontend development server..."
cd frontend
# Use nohup to prevent suspension and redirect output
nohup npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Verify frontend is running
if ! curl -s http://localhost:3000 >/dev/null; then
    echo "⚠️  Frontend might be starting on a different port, check frontend.log"
    echo "📋 Frontend log:"
    tail -10 frontend.log
else
    echo "✅ Frontend is running on http://localhost:3000"
fi

echo "✅ Development environment started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📋 Frontend logs: tail -f frontend.log"

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "🎯 Press Ctrl+C to stop all services"
echo "📋 To view logs: tail -f frontend.log"

# Wait for processes
wait
