#!/bin/bash
echo "Starting AI Abstraction Layer in development mode..."

# Kill any existing processes on ports 8000 and 3000
echo "Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start the backend server (API only)
echo "Starting backend server on http://localhost:8000..."
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait a moment for backend to start
sleep 3

# Start the frontend server
echo "Starting frontend server on http://localhost:3000..."
cd frontend && python3 -m http.server 3000 &

# Wait a moment for frontend to start
sleep 2

echo "✅ AI Abstraction Layer is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📊 Health Check: http://localhost:8000/health"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user to stop
wait
