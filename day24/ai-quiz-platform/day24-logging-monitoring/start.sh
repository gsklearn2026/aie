#!/bin/bash

echo "🚀 Starting AI Quiz Platform - Logging and Monitoring Service"

# Create logs directory
mkdir -p logs

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "⚛️ Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create log files
touch logs/app.log

# Start backend server
echo "🖥️ Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Start frontend development server
echo "🌐 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for stop script
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

echo "✅ All services started successfully!"
echo "📊 Backend API: http://localhost:8080"
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "📈 Metrics: http://localhost:8000"
echo ""
echo "💡 Use './stop.sh' to stop all services"

# Keep script running
wait
