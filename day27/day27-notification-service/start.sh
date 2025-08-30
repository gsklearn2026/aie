#!/bin/bash

echo "🚀 Starting Day 27: Notification Service"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start Redis server (if not running)
echo "🔴 Starting Redis server..."
redis-server --daemonize yes

# Wait for Redis to start
sleep 2

# Start backend server
echo "🐍 Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend server
echo "⚛️ Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔗 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

# Create PID file for stop script
echo "$BACKEND_PID" > backend.pid
echo "$FRONTEND_PID" > frontend.pid

echo "🎯 Testing notification system..."
sleep 10

# Create a test notification
curl -X POST "http://localhost:8000/api/notifications/test-event" \
  -H "Content-Type: application/json"

echo ""
echo "✅ Test notification created! Check the dashboard at http://localhost:3000"
echo "🛑 Run ./stop.sh to stop all services"

# Keep script running
wait
