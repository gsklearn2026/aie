#!/bin/bash

set -e

echo "🚀 Starting Learning Path Generator System"
echo "=========================================="

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "⚛️  Installing React dependencies..."
cd frontend
npm install
cd ..

# Start services with Docker Compose
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo "🗃️  Initializing database..."
cd backend
python -c "
import asyncio
from app.database.connection import init_db
asyncio.run(init_db())
print('Database initialized successfully!')
"
cd ..

# Start backend server
echo "🚀 Starting backend server..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend development server
echo "🌐 Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ System started successfully!"
echo "================================"
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Demo User ID: 1"
echo "🧪 Test the system by:"
echo "   1. Visit http://localhost:3000"
echo "   2. Go to 'Generate Path' tab"
echo "   3. Select topics and generate a path"
echo "   4. View progress in 'Progress' tab"
echo ""
echo "🛑 To stop the system, run: ./stop.sh"

./run_tests.sh


# Save PIDs for cleanup
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

# Keep script running
wait
