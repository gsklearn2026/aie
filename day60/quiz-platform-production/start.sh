#!/bin/bash

echo "Starting Quiz Platform Production..."

echo "Choose startup option:"
echo "1. Start with Docker"
echo "2. Start without Docker (local)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    docker-compose up -d
    echo "All services started!"
    echo "Application: http://localhost"
    echo "Prometheus: http://localhost:9090"
else
    echo "Starting local services..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    
    # Check and create virtual environment if missing
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if dependencies are installed (check for uvicorn)
    if ! python -c "import uvicorn" 2>/dev/null; then
        echo "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo "Python dependencies already installed."
    fi
    
    # Set environment variables
    export DATABASE_URL="postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db"
    export REDIS_URL="redis://localhost:6379"
    
    # Start backend
    echo "Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID)"
    
    # Frontend setup
    echo "Setting up frontend..."
    cd ../frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install
    else
        echo "npm dependencies already installed."
    fi
    
    # Start frontend
    echo "Starting frontend server..."
    npm start &
    FRONTEND_PID=$!
    echo "Frontend started (PID: $FRONTEND_PID)"
    
    cd ..
    echo ""
    echo "Services started!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Note: Make sure PostgreSQL and Redis are running locally"
    echo "To stop services, use: kill $BACKEND_PID $FRONTEND_PID"
fi
