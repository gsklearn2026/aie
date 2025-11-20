#!/bin/bash

set -e

echo "=============================================="
echo "Day 56: Content Refresh - Starting Services"
echo "=============================================="

USE_DOCKER=false
if [[ "$1" == "--docker" ]]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Starting with Docker..."
    docker-compose up -d
    
    echo ""
    echo "Services started:"
    echo "  Backend:  http://localhost:8000"
    echo "  Frontend: http://localhost:3000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs: docker-compose logs -f"
    
else
    echo "Starting local services..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start backend
    echo "Starting backend..."
    cd backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend
    sleep 3
    
    # Seed data
    echo "Seeding data..."
    python scripts/seed_data.py
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "Services started:"
    echo "  Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
    echo "  Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Save PIDs
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
fi
