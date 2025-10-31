#!/bin/bash

# Build script for E2E Testing Setup
set -e

echo "🚀 Building E2E Testing Environment"

# Function to show menu
show_menu() {
    echo ""
    echo "Choose build option:"
    echo "1) Build and run with Docker"
    echo "2) Build and run locally (no Docker)"
    echo "3) Run tests only"
    echo "4) Clean and rebuild"
    echo "q) Quit"
    echo ""
}

# Function to build with Docker
build_with_docker() {
    echo "🐳 Building with Docker..."
    
    # Build and start services
    cd docker
    docker-compose -f docker-compose.e2e.yml build
    docker-compose -f docker-compose.e2e.yml up -d postgres-e2e redis-e2e
    
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    docker-compose -f docker-compose.e2e.yml up -d backend-e2e
    sleep 5
    
    docker-compose -f docker-compose.e2e.yml up -d frontend-e2e
    sleep 5
    
    echo "✅ Services are running!"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
    echo "PostgreSQL: localhost:5432"
    
    # Run E2E tests
    echo "🧪 Running E2E tests..."
    docker-compose -f docker-compose.e2e.yml run --rm e2e-tests
    
    cd ..
}

# Function to build locally
build_locally() {
    echo "🏠 Building locally..."
    
    # Create virtual environment
    python3 -m venv venv-e2e
    source venv-e2e/bin/activate
    
    # Install backend dependencies
    pip install -r backend/requirements.txt
    
    # Install E2E test dependencies
    pip install -r tests/requirements-e2e.txt
    
    # Install Playwright browsers
    playwright install
    
    # Install frontend dependencies
    cd frontend
    npm install
    npm run build
    cd ..
    
    echo "✅ Local build completed!"
    echo ""
    echo "To run the application:"
    echo "1. Start backend: cd backend && uvicorn app.main:app --reload"
    echo "2. Start frontend: cd frontend && npm run dev"
    echo "3. Run E2E tests: pytest tests/ -v"
}

# Function to run tests only
run_tests_only() {
    echo "🧪 Running E2E tests..."
    
    if [ -d "venv-e2e" ]; then
        source venv-e2e/bin/activate
    fi
    
    # Check if services are running
    if curl -f http://localhost:3000 >/dev/null 2>&1 && curl -f http://localhost:8000 >/dev/null 2>&1; then
        pytest tests/e2e/ -v --html=reports/e2e-report.html --self-contained-html
        echo "📊 Test report generated: reports/e2e-report.html"
    else
        echo "❌ Services not running. Please start the application first."
        exit 1
    fi
}

# Function to clean and rebuild
clean_rebuild() {
    echo "🧹 Cleaning previous builds..."
    
    # Stop Docker services
    cd docker
    docker-compose -f docker-compose.e2e.yml down -v
    docker system prune -f
    cd ..
    
    # Remove virtual environment
    rm -rf venv-e2e
    
    # Clean npm cache
    if [ -d "frontend/node_modules" ]; then
        rm -rf frontend/node_modules
    fi
    
    echo "✅ Cleanup completed!"
}

# Main menu loop
while true; do
    show_menu
    read -p "Select option: " choice
    
    case $choice in
        1)
            build_with_docker
            break
            ;;
        2)
            build_locally
            break
            ;;
        3)
            run_tests_only
            break
            ;;
        4)
            clean_rebuild
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
echo "🎉 E2E Testing Environment Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. Configure your GEMINI_API_KEY in environment variables"
echo "2. Run 'bash start.sh' to start all services"
echo "3. Access the dashboard at http://localhost:3000"
echo "4. Run tests with 'pytest tests/e2e/ -v'"
echo ""
