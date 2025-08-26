#!/bin/bash

echo "🚀 Starting AI Quiz Platform - Error Handling Framework"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
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
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start services
echo "🏃 Starting services..."

# Start backend in background
cd backend
export PYTHONPATH=.
python -m src.main &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend in background
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Services started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

# Save PIDs for stop script
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "Press Ctrl+C to stop all services"
wait
