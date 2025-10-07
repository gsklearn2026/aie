#!/bin/bash

set -e

echo "🏗️  Day 40: CD Pipeline Build Script"
echo "===================================="

# Function to display menu
show_menu() {
    echo ""
    echo "Select build option:"
    echo "1) Build with Docker"
    echo "2) Build without Docker (local)"
    echo "3) Run tests only"
    echo "4) Demo deployment"
    echo "5) Exit"
}

# Function to build with Docker
build_with_docker() {
    echo "🐳 Building with Docker..."
    
    # Build backend Docker image
    cd backend
    echo "📦 Building backend Docker image..."
    docker build -t quiz-platform-backend:latest .
    
    # Create network if it doesn't exist
    docker network create quiz-network 2>/dev/null || true
    
    echo "✅ Docker build completed"
    cd ..
}

# Function to build without Docker
build_without_docker() {
    echo "🐍 Building without Docker (local environment)..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install backend dependencies
    cd backend
    pip install -r requirements.txt
    cd ..
    
    echo "✅ Local build completed"
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    
    if command -v docker &> /dev/null && docker images | grep -q quiz-platform-backend; then
        echo "Running tests with Docker..."
        docker run --rm \
            -v $(pwd)/backend:/app \
            quiz-platform-backend:latest \
            python -m pytest tests/ -v
    else
        echo "Running tests locally..."
        cd backend
        if [[ -f "../venv/bin/activate" ]]; then
            source ../venv/bin/activate
        fi
        python -m pytest tests/ -v
        cd ..
    fi
    
    echo "✅ Tests completed"
}

# Function to demo deployment
demo_deployment() {
    echo "🚀 Running deployment demo..."
    
    # Kill any existing containers
    docker stop quiz-backend-staging quiz-backend-green quiz-backend-blue 2>/dev/null || true
    docker rm quiz-backend-staging quiz-backend-green quiz-backend-blue 2>/dev/null || true
    
    echo "📊 Step 1: Deploying to staging..."
    docker run -d \
        --name quiz-backend-staging \
        --network quiz-network \
        -p 8001:8000 \
        -e ENVIRONMENT=staging \
        -e GEMINI_API_KEY=${GEMINI_API_KEY:-"demo-key"} \
        quiz-platform-backend:latest
    
    echo "⏳ Waiting for staging to be ready..."
    sleep 5
    
    echo "🏥 Health check - staging..."
    curl -f http://localhost:8001/health || echo "❌ Staging health check failed"
    
    echo "🟢 Step 2: Blue-Green deployment to production..."
    docker run -d \
        --name quiz-backend-green \
        --network quiz-network \
        -p 8002:8000 \
        -e ENVIRONMENT=production \
        -e GEMINI_API_KEY=${GEMINI_API_KEY:-"demo-key"} \
        quiz-platform-backend:latest
    
    echo "⏳ Waiting for production to be ready..."
    sleep 5
    
    echo "🏥 Health check - production..."
    curl -f http://localhost:8002/health || echo "❌ Production health check failed"
    
    echo "✅ Deployment demo completed!"
    echo ""
    echo "🌐 Services running:"
    echo "   Staging:    http://localhost:8001"
    echo "   Production: http://localhost:8002"
    echo ""
    echo "📊 Test endpoints:"
    echo "   curl http://localhost:8001/health"
    echo "   curl http://localhost:8001/api/deployment/info"
    echo "   curl http://localhost:8002/health"
    echo "   curl http://localhost:8002/api/deployment/info"
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            build_with_docker
            ;;
        2)
            build_without_docker
            ;;
        3)
            run_tests
            ;;
        4)
            demo_deployment
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-5."
            ;;
    esac
done
