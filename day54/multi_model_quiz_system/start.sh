#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "=========================================="
echo "Starting Multi-Model Quiz Generation System"
echo "=========================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null
        sleep 2
    fi
}

# Check for duplicate services
echo "Checking for existing services..."
if check_port 8000; then
    echo "Warning: Port 8000 is already in use. Killing existing process..."
    kill_port 8000
fi

if check_port 3000; then
    echo "Warning: Port 3000 is already in use. Killing existing process..."
    kill_port 3000
fi

# Check for running uvicorn processes
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "Warning: Found existing uvicorn processes. Killing them..."
    pkill -f "uvicorn app.main:app"
    sleep 2
fi

# Check for running react-scripts processes
if pgrep -f "react-scripts start" > /dev/null; then
    echo "Warning: Found existing react-scripts processes. Killing them..."
    pkill -f "react-scripts start"
    sleep 2
fi

echo "Select start option:"
echo "1) Start without Docker"
echo "2) Start with Docker"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "Starting without Docker..."
    
    # Verify paths exist
    BACKEND_DIR="$PROJECT_DIR/backend"
    FRONTEND_DIR="$PROJECT_DIR/frontend"
    VENV_DIR="$BACKEND_DIR/venv"
    
    if [ ! -d "$BACKEND_DIR" ]; then
        echo "Error: Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo "Error: Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "Error: Virtual environment not found. Please run build.sh first."
        exit 1
    fi
    
    # Start Redis (assuming installed)
    echo "Make sure Redis is running on port 6379"
    
    # Start backend
    echo "Starting backend on port 8000..."
    cd "$BACKEND_DIR"
    source "$VENV_DIR/bin/activate"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    cd "$PROJECT_DIR"
    
    # Wait a bit for backend to start
    sleep 3
    
    # Check if backend started successfully
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Error: Backend failed to start. Check backend.log for details."
        exit 1
    fi
    
    # Start frontend
    echo "Starting frontend on port 3000..."
    cd "$FRONTEND_DIR"
    REACT_APP_API_URL=http://localhost:8000 npm start > "$PROJECT_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    cd "$PROJECT_DIR"
    
    echo "Services started!"
    echo "Backend PID: $BACKEND_PID (logs: $PROJECT_DIR/backend.log)"
    echo "Frontend PID: $FRONTEND_PID (logs: $PROJECT_DIR/frontend.log)"
    echo "Access application at http://localhost:3000"
    echo "API docs at http://localhost:8000/docs"
    echo ""
    echo "To stop services, run: ./stop.sh"
    
    wait
    
elif [ "$choice" = "2" ]; then
    echo "Starting with Docker..."
    cd "$PROJECT_DIR"
    if [ ! -f "docker-compose.yml" ]; then
        echo "Error: docker-compose.yml not found. Please run build.sh first with Docker option."
        exit 1
    fi
    docker-compose up
    
else
    echo "Invalid choice"
    exit 1
fi
