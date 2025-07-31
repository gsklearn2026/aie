#!/bin/bash

set -e

echo "🚀 Starting Progressive Difficulty Quiz Platform"
echo "=============================================="

echo "🐍 Starting with Python virtual environment (no Docker)"

# Create virtual environment with Python 3.11
echo "📦 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📱 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start PostgreSQL and Redis (assuming they're installed)
echo "🗄️ Starting database services..."
if command -v brew &> /dev/null; then
    # macOS with Homebrew
    brew services start postgresql
    brew services start redis
elif command -v systemctl &> /dev/null; then
    # Linux with systemd
    sudo systemctl start postgresql
    sudo systemctl start redis
else
    echo "⚠️ Please start PostgreSQL and Redis manually"
    echo "PostgreSQL should be running on port 5432"
    echo "Redis should be running on port 6379"
fi

# Wait for services
sleep 5

# Create database
echo "🏗️ Setting up database..."
cd backend
python -c "
from app.models.difficulty import Base
from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db'))
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Start backend
echo "🔧 Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start frontend
echo "📱 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "✅ Platform started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the platform, run: ./stop.sh"
