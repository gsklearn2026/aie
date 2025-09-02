#!/bin/bash

echo "🚀 Starting Quiz Export Service Development Environment"

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
python3 -m venv quiz-export-env
source quiz-export-env/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
pip install faker  # For sample data generation
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database and generate sample data
echo "🗄️ Initializing database and generating sample data..."
cd backend
python scripts/generate_sample_data.py
cd ..

# Start backend
echo "🖥️ Starting backend server..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start Celery worker
echo "👷 Starting Celery worker..."
cd backend
celery -A app.celery_tasks.worker:celery_app worker --loglevel=info &
CELERY_PID=$!
cd ..

# Start frontend
echo "🌐 Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $CELERY_PID > .celery.pid  
echo $FRONTEND_PID > .frontend.pid

echo "✅ All services started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop all services, run: ./stop.sh"

# Wait for user input
echo "Press Ctrl+C to stop all services..."
wait
