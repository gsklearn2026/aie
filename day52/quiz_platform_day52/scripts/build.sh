#!/bin/bash

echo "🏗️  Building Quiz Platform - Day 52"

# Ask for Docker or local
echo "Choose build option:"
echo "1) With Docker"
echo "2) Without Docker (local)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo "🐳 Building with Docker..."
    
    # Create Dockerfile for backend
    cat > backend/Dockerfile << 'DOCKERFILE_END'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE_END

    # Create docker-compose.yml
    cat > docker-compose.yml << 'DOCKER_COMPOSE_END'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./backend:/app
  
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
DOCKER_COMPOSE_END

    # Frontend Dockerfile
    cat > frontend/Dockerfile << 'DOCKERFILE_END'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
DOCKERFILE_END

    docker-compose build
    echo "✅ Docker build complete"
    
else
    echo "💻 Building locally..."
    
    # Backend setup
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend setup
    cd frontend
    npm install
    cd ..
    
    echo "✅ Local build complete"
fi

echo ""
echo "✅ Build completed successfully!"
echo "Run './scripts/start.sh' to start the application"
