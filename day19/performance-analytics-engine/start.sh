#!/bin/bash

echo "🚀 Starting Performance Analytics Engine..."

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/quiz_platform"
export REDIS_URL="redis://localhost:6379/0"
export GEMINI_API_KEY="Your key"

# Start services with Docker Compose
echo "🐳 Starting services with Docker..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Start backend
echo "🔧 Starting backend service..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
sleep 5

# Start frontend
echo "🎨 Starting frontend service..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Performance Analytics Engine is running!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"

# Create demo data
sleep 10
echo "🎭 Creating demo data..."
curl -X POST "http://localhost:8000/api/v1/analytics/create-demo-data" \
  -H "Content-Type: application/json"

echo "📊 Demo data created! Visit http://localhost:3000 to see the analytics dashboard."

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

wait
