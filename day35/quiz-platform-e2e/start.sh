#!/bin/bash

# Start script for E2E Testing Environment
set -e

echo "🚀 Starting E2E Testing Environment"

# Function to show menu
show_menu() {
    echo ""
    echo "Choose startup option:"
    echo "1) Start with Docker"
    echo "2) Start locally"
    echo "3) Start tests only"
    echo "q) Quit"
    echo ""
}

# Function to start with Docker
start_with_docker() {
    echo "🐳 Starting with Docker..."
    
    cd docker
    docker-compose -f docker-compose.e2e.yml up -d
    
    echo "⏳ Waiting for services to be ready..."
    
    # Wait for backend to be ready
    timeout=60
    counter=0
    while ! curl -f http://localhost:8000/health >/dev/null 2>&1; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            echo "❌ Backend failed to start within $timeout seconds"
            exit 1
        fi
        echo "Waiting for backend... ($counter/$timeout seconds)"
    done
    
    # Wait for frontend to be ready
    counter=0
    while ! curl -f http://localhost:3000 >/dev/null 2>&1; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            echo "❌ Frontend failed to start within $timeout seconds"
            exit 1
        fi
        echo "Waiting for frontend... ($counter/$timeout seconds)"
    done
    
    cd ..
    
    echo "✅ All services are running!"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
    echo "Backend Health: http://localhost:8000/health"
    echo ""
    echo "🧪 You can now run E2E tests with: pytest tests/e2e/ -v"
}

# Function to start locally
start_locally() {
    echo "🏠 Starting locally..."
    
    # Activate virtual environment
    if [ ! -d "venv-e2e" ]; then
        echo "❌ Virtual environment not found. Please run build.sh first."
        exit 1
    fi
    
    source venv-e2e/bin/activate
    
    # Start services in background
    echo "Starting backend..."
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    echo "Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "✅ Services started locally!"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
    echo ""
    echo "To stop services, run: bash stop.sh"
}

# Function to run tests only
start_tests_only() {
    echo "🧪 Starting E2E test suite..."
    
    if [ -d "venv-e2e" ]; then
        source venv-e2e/bin/activate
    fi
    
    # Run comprehensive E2E tests
    pytest tests/e2e/ -v \
        --html=reports/e2e-report.html \
        --self-contained-html \
        --tb=short \
        --maxfail=5
    
    echo "📊 Test report generated: reports/e2e-report.html"
    
    # Run performance tests separately
    echo "📈 Running performance tests..."
    pytest tests/e2e/performance/ -v -m performance
    
    # Run visual regression tests
    echo "👁️ Running visual regression tests..."
    pytest tests/e2e/visual_regression/ -v -m visual
}

# Main menu loop
while true; do
    show_menu
    read -p "Select option: " choice
    
    case $choice in
        1)
            start_with_docker
            break
            ;;
        2)
            start_locally
            break
            ;;
        3)
            start_tests_only
            break
            ;;
        q|Q)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
done

echo ""
echo "🎉 E2E Testing Environment is running!"
echo ""
echo "Available Commands:"
echo "• View logs: docker-compose -f docker/docker-compose.e2e.yml logs -f"
echo "• Run specific test: pytest tests/e2e/user_journeys/test_quiz_completion.py -v"
echo "• Run with browser visible: pytest tests/e2e/ --headed"
echo "• Generate new baseline screenshots: pytest tests/e2e/visual_regression/ --update-snapshots"
echo ""
