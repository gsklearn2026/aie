#!/bin/bash

echo "🏗️ Building Quiz Platform API Versioning System"
echo "================================================"

# Check if Docker is available
DOCKER_AVAILABLE=false
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    DOCKER_AVAILABLE=true
    echo "✅ Docker is available"
else
    echo "⚠️ Docker not available or not running"
fi

echo "Choose build option:"
echo "1) Local Python environment"
echo "2) Docker environment"
echo -n "Enter choice (1 or 2): "
read choice

if [ "$choice" = "2" ] && [ "$DOCKER_AVAILABLE" = false ]; then
    echo "❌ Docker not available. Falling back to local build."
    choice="1"
fi

if [ "$choice" = "1" ]; then
    echo "🐍 Building with local Python environment..."
    
    # Backend setup
    echo "📦 Setting up backend environment..."
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Backend setup complete"
    cd ..
    
    # Frontend setup
    echo "⚛️ Setting up frontend environment..."
    cd frontend
    
    # Install Node dependencies
    npm install
    
    echo "✅ Frontend setup complete"
    cd ..
    
elif [ "$choice" = "2" ]; then
    echo "🐳 Building with Docker..."
    
    # Create Dockerfile for backend
    cat > backend/Dockerfile << 'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
DOCKERFILE

    # Create Dockerfile for frontend
    cat > frontend/Dockerfile << 'DOCKERFILE'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
DOCKERFILE

    # Create docker-compose.yml
    cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./backend:/app
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    environment:
      - CHOKIDAR_USEPOLLING=true
COMPOSE

    echo "🐳 Building Docker containers..."
    docker-compose build
    
    echo "✅ Docker build complete"
fi

echo ""
echo "🧪 Running tests..."

if [ "$choice" = "1" ]; then
    cd backend
    source venv/bin/activate
    python -m pytest tests/ -v
    cd ..
elif [ "$choice" = "2" ]; then
    docker-compose run --rm backend python -m pytest tests/ -v
fi

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
if [ "$choice" = "1" ]; then
    echo "  Run './start.sh 1' to start with local environment"
elif [ "$choice" = "2" ]; then
    echo "  Run './start.sh 2' to start with Docker"
fi
echo "  Open http://localhost:3000 to view the dashboard"
echo "  API documentation: http://localhost:8000/docs"
