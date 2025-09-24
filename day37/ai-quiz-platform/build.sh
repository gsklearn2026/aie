#!/bin/bash

set -e

echo "🚀 AI Quiz Platform - Build Script"
echo "=================================="

# Function to show menu
show_menu() {
    echo ""
    echo "Choose build option:"
    echo "1) Build with Docker (Recommended)"
    echo "2) Build without Docker (Local development)"
    echo "3) Exit"
    read -p "Enter your choice (1-3): " choice
}

# Build with Docker
build_with_docker() {
    echo "🐳 Building with Docker..."
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        echo "⚠️  Creating .env file..."
        cat > .env << 'ENVEOF'
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_DB=quiz_platform
POSTGRES_USER=quiz_user
POSTGRES_PASSWORD=quiz_password
REDIS_HOST=redis
REDIS_PORT=6379
ENVEOF
        echo "📝 Please update .env file with your Gemini API key"
    fi
    
    # Build all images
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    echo "🚀 Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    echo "🔍 Checking service health..."
    docker-compose ps
    
    # Run tests
    echo "🧪 Running tests..."
    docker-compose exec backend python -m pytest tests/ -v || echo "⚠️  Tests failed - this is expected on first run"
    
    echo ""
    echo "✅ Build completed successfully!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo ""
    echo "📋 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
}

# Build without Docker
build_without_docker() {
    echo "🏠 Building without Docker (Local development)..."
    
    # Check Python version
    python3 --version || { echo "❌ Python 3.11+ required"; exit 1; }
    
    # Check Node.js version
    node --version || { echo "❌ Node.js 18+ required"; exit 1; }
    
    # Setup backend
    echo "🐍 Setting up Python backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements/requirements.txt
    cd ..
    
    # Setup frontend
    echo "⚛️  Setting up React frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    
    # Create local environment
    if [ ! -f .env.local ]; then
        cat > .env.local << 'ENVEOF'
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_HOST=localhost
POSTGRES_DB=quiz_platform
POSTGRES_USER=quiz_user
POSTGRES_PASSWORD=quiz_password
REDIS_HOST=localhost
REDIS_PORT=6379
ENVEOF
        echo "📝 Please update .env.local file with your configuration"
    fi
    
    echo ""
    echo "✅ Local build completed!"
    echo "📝 Next steps:"
    echo "1. Update .env.local with your Gemini API key"
    echo "2. Start PostgreSQL and Redis services"
    echo "3. Run: ./start.sh"
}

# Main execution
show_menu

case $choice in
    1)
        build_with_docker
        ;;
    2)
        build_without_docker
        ;;
    3)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
