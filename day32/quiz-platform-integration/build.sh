#!/bin/bash

set -e

echo "🏗️  Building Quiz Platform Integration Testing Environment"
echo "========================================================"

# Function to show options
show_options() {
    echo ""
    echo "Build Options:"
    echo "1. Local build (without Docker)"
    echo "2. Docker build"
    echo "3. Full build with tests"
    echo ""
    read -p "Select option (1-3): " choice
    echo ""
}

# Local build function
build_local() {
    echo "📦 Building locally..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    cd backend
    pip install -r requirements/base.txt
    cd ..
    
    echo "✅ Local build complete!"
    echo "Next: Run './start.sh' to start services"
}

# Docker build function
build_docker() {
    echo "🐳 Building with Docker..."
    
    # Build backend image
    cd backend
    docker build -t quiz-platform-api .
    cd ..
    
    # Start test environment
    cd docker
    docker-compose -f docker-compose.test.yml up -d postgres redis
    cd ..
    
    echo "✅ Docker build complete!"
    echo "Next: Run './start.sh' to start all services"
}

# Full build with tests
build_full() {
    echo "🔧 Full build with integration tests..."
    
    # Local build first
    build_local
    
    # Setup test database
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost/test_quizdb"
    
    # Start test services
    cd docker
    docker-compose -f docker-compose.test.yml up -d
    sleep 10
    cd ..
    
    # Run integration tests
    cd backend
    source ../venv/bin/activate
    python -m pytest src/tests/integration/ -v
    cd ..
    
    echo "✅ Full build with tests complete!"
    echo "📊 Integration test results above ☝️"
}

# Main execution
show_options

case $choice in
    1)
        build_local
        ;;
    2)
        build_docker
        ;;
    3)
        build_full
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Build completed successfully!"
echo "📖 Check README.md for next steps"
