#!/bin/bash

echo "🚀 Starting Day 22: Caching Implementation Demo"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "⚛️ Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 5

# Start backend
echo "🖥️ Starting backend server..."
cd backend
source ../venv/bin/activate
python -m pytest src/tests/ -v
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🌐 Starting frontend..."
cd frontend
npm test -- --watchAll=false
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started successfully!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API Docs:   http://localhost:8000/docs"
echo "   Cache Statistics:   http://localhost:8000/api/v1/cache/stats"
echo "   Health Check:       http://localhost:8000/health"
echo ""
echo "🧪 Demo Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Load Quiz Data' multiple times to see caching in action"
echo "3. Monitor response times - first request may be slower (cache miss)"
echo "4. Subsequent requests should be faster (cache hits)"
echo "5. Click 'Clear Cache' and try loading again to see cache miss"
echo "6. Visit Cache Monitor tab to see detailed statistics"
echo ""
echo "📊 Watch for:"
echo "   - Response times under 100ms (cache hits)"
echo "   - Cache hit rates above 75%"
echo "   - Memory usage in Redis"
echo ""
echo "💡 To stop all services, run: ./stop.sh"

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

# Keep script running
wait
