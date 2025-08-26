#!/bin/bash

echo "🛑 Stopping Progressive Difficulty Quiz Platform"
echo "============================================="

echo "🐍 Stopping local services..."

# Stop backend
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm backend.pid
fi

# Stop frontend
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm frontend.pid
fi

# Stop database services if started by us
if command -v brew &> /dev/null; then
    echo "Stopping PostgreSQL and Redis..."
    brew services stop postgresql || true
    brew services stop redis || true
fi

echo "✅ Platform stopped successfully!"
