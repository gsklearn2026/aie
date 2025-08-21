#!/bin/bash

echo "🛑 Stopping Learning Path Generator System"
echo "==========================================="

# Function to kill process by port
kill_process_on_port() {
    local port=$1
    local process_name=$2
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "🔴 Stopping $process_name on port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null
        sleep 1
        # Double check if still running
        if lsof -ti:$port >/dev/null 2>&1; then
            echo "⚠️  Force killing $process_name on port $port..."
            kill -9 $(lsof -ti:$port) 2>/dev/null
        fi
    else
        echo "✅ No $process_name running on port $port"
    fi
}

# Kill backend if running
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🐍 Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "⚠️  Force killing backend..."
            kill -9 $BACKEND_PID
        fi
    fi
    rm -f .backend_pid
fi

# Kill frontend if running
if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚛️  Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        # Force kill if still running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "⚠️  Force killing frontend..."
            kill -9 $FRONTEND_PID
        fi
    fi
    rm -f .frontend_pid
fi

# Kill any processes running on specific ports
echo "🔍 Checking for processes on specific ports..."
kill_process_on_port 8000 "Backend API"
kill_process_on_port 3000 "Frontend React"
kill_process_on_port 5432 "PostgreSQL"
kill_process_on_port 6379 "Redis"
kill_process_on_port 5555 "Flower (Celery monitoring)"

# Kill any Python processes related to our app
echo "🐍 Checking for Python processes..."
PYTHON_PIDS=$(pgrep -f "uvicorn.*main:app\|python.*main.py\|celery.*worker" 2>/dev/null)
if [ ! -z "$PYTHON_PIDS" ]; then
    echo "🔴 Stopping Python processes: $PYTHON_PIDS"
    echo $PYTHON_PIDS | xargs kill -9 2>/dev/null
fi

# Kill any Node processes related to our frontend
echo "📦 Checking for Node processes..."
NODE_PIDS=$(pgrep -f "react-scripts\|node.*3000" 2>/dev/null)
if [ ! -z "$NODE_PIDS" ]; then
    echo "🔴 Stopping Node processes: $NODE_PIDS"
    echo $NODE_PIDS | xargs kill -9 2>/dev/null
fi

# Stop Docker services
echo "🐳 Stopping Docker services..."
docker-compose down 2>/dev/null

# Clean up any temporary files
echo "🧹 Cleaning up temporary files..."
rm -f .backend_pid .frontend_pid .celery_pid

# Wait a moment for processes to fully stop
sleep 2

# Final check for any remaining processes on our ports
echo "🔍 Final port check..."
for port in 8000 3000 5432 6379 5555; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "⚠️  Process still running on port $port, force killing..."
        kill -9 $(lsof -ti:$port) 2>/dev/null
    fi
done

echo "✅ System stopped successfully!"
echo "🎯 All processes and ports have been cleared"
