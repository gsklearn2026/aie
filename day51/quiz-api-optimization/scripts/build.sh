#!/bin/bash

echo "========================================"
echo "Building Quiz API Optimization System"
echo "========================================"

# Check if Docker option is selected
USE_DOCKER=false
if [ "$1" == "--docker" ]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Building with Docker..."
    
    # Create Dockerfile for backend
    cat > Dockerfile.backend << 'DOCKEREOF'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

CMD ["python", "-m", "uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKEREOF

    # Create Dockerfile for frontend
    cat > Dockerfile.frontend << 'DOCKEREOF'
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

CMD ["npm", "start"]
DOCKEREOF

    # Create docker-compose
    cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
DOCKEREOF

    docker-compose build
    echo "✅ Docker build complete!"
    
else
    echo "Building without Docker..."
    
    # Backend setup
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    
    # Frontend setup
    cd frontend
    npm install
    cd ..
    
    echo "✅ Build complete!"
fi

echo ""
echo "Next steps:"
if [ "$USE_DOCKER" = true ]; then
    echo "  Run: ./scripts/start.sh --docker"
else
    echo "  Run: ./scripts/start.sh"
fi
