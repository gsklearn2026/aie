#!/bin/bash
set -e

echo "🚀 Day 53: Connection Pooling - Build Script"
echo "============================================="

show_menu() {
    echo ""
    echo "Select build option:"
    echo "1) Build and run with Docker"
    echo "2) Build and run without Docker (local)"
    echo "3) Run tests"
    echo "4) Exit"
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1) build_with_docker ;;
        2) build_without_docker ;;
        3) run_tests ;;
        4) exit 0 ;;
        *) echo "Invalid option"; show_menu ;;
    esac
}

build_with_docker() {
    echo "🐳 Building with Docker..."
    
    # Start services
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Setup backend
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Backend dependencies installed"
    
    # Setup frontend
    cd ../frontend
    npm install
    
    echo "✅ Frontend dependencies installed"
    echo "✅ Build complete with Docker!"
    
    cd ..
    ./start.sh docker
}

build_without_docker() {
    echo "💻 Building without Docker (local PostgreSQL required)..."
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        echo "❌ PostgreSQL not found. Please install PostgreSQL or use Docker option."
        exit 1
    fi
    
    # Setup database
    echo "Setting up database..."
    psql -U postgres -c "CREATE DATABASE quizdb;" 2>/dev/null || true
    psql -U postgres -c "CREATE USER quizuser WITH PASSWORD 'quizpass';" 2>/dev/null || true
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE quizdb TO quizuser;" 2>/dev/null || true
    
    # Check Redis
    if ! command -v redis-cli &> /dev/null; then
        echo "⚠️  Redis not found. Install Redis or use Docker option."
    fi
    
    # Setup backend
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Backend dependencies installed"
    
    # Setup frontend
    cd ../frontend
    npm install
    
    echo "✅ Frontend dependencies installed"
    echo "✅ Build complete!"
    
    cd ..
    ./start.sh local
}

run_tests() {
    echo "🧪 Running tests..."
    
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    pytest tests/ -v
    
    echo "✅ Tests completed!"
    cd ..
}

show_menu
