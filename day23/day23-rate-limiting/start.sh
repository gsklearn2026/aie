#!/bin/bash

echo "🚀 Starting AI Quiz Platform with Rate Limiting..."

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis server..."
    redis-server --daemonize yes --port 6379
    sleep 2
fi

# Setup Python virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Run tests
echo "Running tests..."
source venv/bin/activate
python -m pytest tests/ -v

# Start backend
echo "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Setup complete!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:5000"
echo "📈 Rate Limits Monitor: http://localhost:3000/rate-limits"

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "Press Ctrl+C to stop all services"
wait
