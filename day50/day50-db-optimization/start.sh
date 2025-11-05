#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Starting Quiz Platform ==="

# Start PostgreSQL in Docker if docker-compose.yml exists
if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
    echo "Starting PostgreSQL with Docker..."
    docker-compose up -d postgres 2>/dev/null || true
    echo "Waiting for PostgreSQL to be ready..."
    sleep 3
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        echo "✓ PostgreSQL is ready"
    else
        echo "⚠️  PostgreSQL may still be starting..."
    fi
    echo ""
fi

# Start backend and frontend locally
if [ ! -f "$SCRIPT_DIR/docker-compose.yml" ] || [ "$1" != "--docker-only" ]; then
    echo "Starting without Docker..."
    
    # Check database connection
    echo "Checking database connection..."
    cd "$SCRIPT_DIR/backend"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        # Test database connection
        python -c "
import sys
from sqlalchemy import create_engine, text
import os

# Check if DATABASE_URL is set (from Docker PostgreSQL), otherwise use default
DATABASE_URL = os.getenv('DATABASE_URL') or 'postgresql://quizuser:quizpass@localhost:5433/quizdb'
try:
    engine = create_engine(DATABASE_URL, connect_args={'connect_timeout': 2})
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✓ Database connection successful')
except Exception as e:
    print('❌ Database connection failed:', str(e))
    print('')
    print('Please run ./setup-db.sh to set up the database, or manually create:')
    print('  Database: quizdb')
    print('  User: quizuser')
    print('  Password: quizpass')
    sys.exit(1)
" 2>&1
        if [ $? -ne 0 ]; then
            echo ""
            echo "Database setup required. Run: ./setup-db.sh"
            exit 1
        fi
        deactivate
    fi
    cd "$SCRIPT_DIR"
    
    # Start backend
    echo "Starting backend..."
    cd "$SCRIPT_DIR/backend"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Please run build.sh first."
        exit 1
    fi
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd "$SCRIPT_DIR"
    
    # Start frontend
    echo "Starting frontend..."
    cd "$SCRIPT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        echo "Error: node_modules not found. Please run build.sh first."
        exit 1
    fi
    HOST=0.0.0.0 PORT=3000 npm start &
    FRONTEND_PID=$!
    cd "$SCRIPT_DIR"
    
    # Save PIDs
    echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
    echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
    
    echo ""
    echo "✓ Application started!"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend: http://localhost:8000"
    echo ""
    echo "To stop: ./stop.sh"
fi
