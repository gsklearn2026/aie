#!/bin/bash

echo "🚀 Building Quiz Taking Interface System..."

# Function to choose build method
choose_build_method() {
    echo "Choose build method:"
    echo "1) Docker (Recommended)"
    echo "2) Local Development"
    read -p "Enter choice (1-2): " choice
    
    case $choice in
        1) build_with_docker ;;
        2) build_local ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
}

# Docker build
build_with_docker() {
    echo "📦 Building with Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Build and start services
    docker-compose build --no-cache
    docker-compose up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Test backend
    echo "🧪 Testing backend..."
    curl -f http://localhost:8000/api/health || echo "⚠️ Backend health check failed"
    
    echo "✅ Docker build complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
}

# Local build
build_local() {
    echo "💻 Building locally..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found"
        exit 1
    fi
    
    # Setup backend
    echo "🐍 Setting up Python backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Test backend
    echo "🧪 Testing backend..."
    python -m pytest tests/ -v
    
    # Start backend in background
    echo "🚀 Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    cd ..
    
    # Setup frontend
    echo "⚛️ Setting up React frontend..."
    cd frontend
    npm install
    
    # Test frontend
    echo "🧪 Testing frontend..."
    npm test -- --run --watchAll=false
    
    # Build frontend
    echo "🔨 Building frontend..."
    npm run build
    
    # Start frontend
    echo "🚀 Starting frontend server..."
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Test endpoints
    echo "🧪 Testing API endpoints..."
    curl -f http://localhost:8000/api/health || echo "⚠️ Backend health check failed"
    
    echo "✅ Local build complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend_pid
    echo $FRONTEND_PID > .frontend_pid
}

# Run tests
run_tests() {
    echo "🧪 Running comprehensive tests..."
    
    # Backend tests
    cd backend
    python -m pytest tests/ -v --tb=short
    cd ..
    
    # Frontend tests
    cd frontend
    npm test -- --run --watchAll=false
    cd ..
    
    echo "✅ All tests completed!"
}

# Demo function
demo() {
    echo "🎬 Starting demo..."
    echo ""
    echo "📋 Demo Instructions:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Select 'AI Engineering Fundamentals' quiz"
    echo "3. Answer the questions (AI-generated content!)"
    echo "4. View detailed results with AI feedback"
    echo "5. Try different quiz types"
    echo ""
    echo "🔧 Technical Features Demonstrated:"
    echo "✅ Real-time quiz session management"
    echo "✅ AI-powered question generation (Gemini)"
    echo "✅ Interactive question presentation"
    echo "✅ Progress tracking with timer"
    echo "✅ Intelligent result analysis"
    echo "✅ Responsive design"
    echo ""
    echo "Press Ctrl+C to stop the demo"
    
    # Keep script running for demo
    while true; do
        sleep 30
        echo "📊 Demo still running... (Ctrl+C to exit)"
    done
}

# Main execution
case "${1:-build}" in
    "build") choose_build_method ;;
    "test") run_tests ;;
    "demo") demo ;;
    "docker") build_with_docker ;;
    "local") build_local ;;
    *) 
        echo "Usage: $0 [build|test|demo|docker|local]"
        echo "  build  - Interactive build selection"
        echo "  test   - Run all tests"
        echo "  demo   - Start demo mode"
        echo "  docker - Build with Docker"
        echo "  local  - Build locally"
        ;;
esac
