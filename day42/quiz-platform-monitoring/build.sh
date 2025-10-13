#!/bin/bash

echo "🚀 Building Quiz Platform Monitoring System"
echo "==========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker availability
check_docker() {
    if command_exists docker && command_exists docker-compose; then
        echo "✅ Docker and Docker Compose found"
        return 0
    else
        echo "❌ Docker or Docker Compose not found"
        return 1
    fi
}

# Build without Docker
build_native() {
    echo "📦 Building native setup..."
    
    # Backend setup
    echo "Setting up Python backend..."
    cd backend
    python -m venv venv
    source venv/bin/activate || source venv/Scripts/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend setup
    echo "Setting up React frontend..."
    cd frontend
    npm install
    cd ..
    
    echo "✅ Native build completed!"
}

# Build with Docker
build_docker() {
    echo "🐳 Building Docker setup..."
    docker-compose build
    echo "✅ Docker build completed!"
}

# Run tests
run_tests() {
    echo "🧪 Running tests..."
    
    if check_docker; then
        echo "Running backend tests..."
        docker-compose run --rm backend python -m pytest tests/ -v
    else
        echo "Running native tests..."
        cd backend
        source venv/bin/activate || source venv/Scripts/activate
        python -m pytest tests/ -v
        cd ..
        
        cd frontend
        npm test -- --coverage --watchAll=false
        cd ..
    fi
    
    echo "✅ Tests completed!"
}

# Start services
start_services() {
    if check_docker; then
        echo "🐳 Starting Docker services..."
        docker-compose up -d
        echo "✅ Services started!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "📊 Backend API: http://localhost:8000"
        echo "📈 Prometheus: http://localhost:9090"
        echo "📊 Grafana: http://localhost:3001 (admin/admin)"
    else
        echo "🖥️  Starting native services..."
        echo "Use start.sh script to run services"
    fi
}

# Demo the application
demo() {
    echo "🎯 Running demo..."
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Click 'Simulate Load' to generate test traffic"
    echo "3. Click 'Test Alerting' to trigger alerts"
    echo "4. Watch real-time metrics update"
    echo "5. Check Prometheus metrics at http://localhost:9090"
    echo "6. View Grafana dashboards at http://localhost:3001"
}

# Main menu
show_menu() {
    echo ""
    echo "Select build option:"
    echo "1) Build with Docker (recommended)"
    echo "2) Build natively (requires Python 3.11+ and Node.js 18+)"
    echo "3) Run tests"
    echo "4) Start services"
    echo "5) Demo"
    echo "6) Exit"
}

# Main execution
main() {
    # Check if running non-interactively (no TTY)
    if [ ! -t 0 ]; then
        echo "🔧 Running in non-interactive mode - executing full build process..."
        if check_docker; then
            build_docker
            start_services
            echo "✅ Build completed! Services should be running."
        else
            echo "❌ Docker not available. Install Docker first."
            exit 1
        fi
        return
    fi
    
    # Interactive mode
    while true; do
        show_menu
        read -p "Enter choice [1-6]: " choice
        
        case $choice in
            1)
                if check_docker; then
                    build_docker
                    start_services
                    demo
                else
                    echo "❌ Docker not available. Install Docker first."
                fi
                ;;
            2)
                build_native
                ;;
            3)
                run_tests
                ;;
            4)
                start_services
                ;;
            5)
                demo
                ;;
            6)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please try again."
                ;;
        esac
    done
}

main
