#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

echo "=============================================="
echo "Day 56: Content Refresh - Build Script"
echo "=============================================="
echo ""

# Check for Docker mode
USE_DOCKER=false
if [[ "$1" == "--docker" ]]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Building with Docker..."
    
    # Build and start containers
    docker-compose build
    docker-compose up -d
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 10
    
    # Run migrations
    docker-compose exec -T backend python -c "
from app.core.database import engine, Base
import asyncio
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"
    
    # Seed data
    docker-compose exec -T -e API_URL=http://backend:8000 backend python /scripts/seed_data.py
    
    # Run tests
    docker-compose exec -T backend pytest tests/ -v
    
    print_status "Docker build complete!"
    echo ""
    echo "Services running:"
    echo "  Backend:  http://localhost:8000"
    echo "  Frontend: http://localhost:3000"
    echo "  API Docs: http://localhost:8000/docs"
    
else
    echo "Building without Docker (local development)..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    source venv/bin/activate
    
    # Install backend dependencies
    cd backend
    pip install -r requirements.txt -q
    print_status "Backend dependencies installed"
    
    # Check PostgreSQL
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        print_warning "PostgreSQL not running. Please start PostgreSQL."
        echo "  On macOS: brew services start postgresql"
        echo "  On Linux: sudo systemctl start postgresql"
        exit 1
    fi
    
    # Create database
    psql -h localhost -U postgres -c "CREATE DATABASE quiz_content;" 2>/dev/null || true
    psql -h localhost -U postgres -c "CREATE DATABASE quiz_content_test;" 2>/dev/null || true
    print_status "Databases created"
    
    # Run tests
    echo ""
    echo "Running tests..."
    pytest tests/ -v --tb=short
    print_status "Tests passed"
    
    cd ..
    
    # Install frontend dependencies
    cd frontend
    npm install --silent
    print_status "Frontend dependencies installed"
    cd ..
    
    print_status "Build complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./start.sh"
    echo "  2. Open: http://localhost:3000"
fi
