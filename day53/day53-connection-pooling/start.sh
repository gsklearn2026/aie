#!/bin/bash
set -e

MODE=${1:-local}

echo "🚀 Starting Quiz Platform - Day 53"
echo "Mode: $MODE"

if [ "$MODE" = "docker" ]; then
    echo "Starting with Docker services..."
    docker-compose up -d
    sleep 5
fi

# Start backend
echo "🔧 Starting backend..."
cd backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 5

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started successfully!"
echo "=================================="
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Pool Metrics available at: http://localhost:3000 (click 'Pool Metrics' tab)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose down 2>/dev/null; exit" INT
wait
