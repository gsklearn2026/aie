#!/bin/bash

echo "🚀 Building Quiz Management Platform"
echo "===================================="

# Check if Docker option is provided
USE_DOCKER=${1:-false}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Building with Docker..."
    
    # Create Docker files
    cat > Dockerfile.backend << 'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE

    cat > Dockerfile.frontend << 'DOCKERFILE'
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .

RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
DOCKERFILE

    cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: quiz_db
      POSTGRES_USER: quiz_user
      POSTGRES_PASSWORD: quiz_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://quiz_user:quiz_password@db:5432/quiz_db
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
COMPOSE

    docker-compose up --build -d
    
else
    echo "🔨 Building locally..."
    
    # Create virtual environment for backend
    echo "Setting up Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install frontend dependencies
    echo "Installing frontend dependencies..."
    cd ../frontend
    npm install
    
    # Build frontend
    echo "Building frontend..."
    npm run build
    
    cd ..
    
    echo "✅ Build completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Run ./start.sh to start the application"
    echo "2. Run ./start.sh docker to use Docker"
fi
