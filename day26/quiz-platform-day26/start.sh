#!/bin/bash

echo "🚀 Starting Quiz Platform - Day 26: Background Job Processing"

# Check if .env exists and has API key
if [ ! -f backend/.env ]; then
    echo "❌ backend/.env file not found!"
    exit 1
fi

if ! grep -q "GEMINI_API_KEY=your_gemini_api_key_here" backend/.env; then
    echo "⚠️  Please update your GEMINI_API_KEY in backend/.env"
    echo "Get your API key from: https://aistudio.google.com/app/apikey"
    read -p "Press Enter to continue anyway..."
fi

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate

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

# Start services with Docker
echo "🐳 Starting Docker services..."
cd docker
docker-compose down
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for database and Redis..."
sleep 10

# Start backend
echo "🖥️  Starting backend server..."
cd ../backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Celery worker
echo "👷 Starting Celery worker..."
python -m celery -A app.core.celery_app worker --loglevel=info &
WORKER_PID=$!

# Start Flower monitoring
echo "🌸 Starting Flower monitoring..."
python -m celery -A app.core.celery_app flower --port=5555 &
FLOWER_PID=$!

# Wait for backend to start
sleep 5

# Run tests
echo "🧪 Running backend tests..."
python -m pytest tests/ -v

# Start frontend
echo "🎨 Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ All services started successfully!"
echo ""
echo "🌐 Access points:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Flower:      http://localhost:5555"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Test the application:"
echo "   1. Go to http://localhost:3000"
echo "   2. Create a quiz generation job"
echo "   3. Monitor progress in real-time"
echo "   4. Check Flower dashboard for worker stats"
echo ""
echo "⚠️  Remember to set your GEMINI_API_KEY in backend/.env"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID $WORKER_PID $FLOWER_PID $FRONTEND_PID > .pids

echo "Press Ctrl+C to stop all services"
wait
