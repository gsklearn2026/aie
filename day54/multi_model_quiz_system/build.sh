#!/bin/bash

echo "=========================================="
echo "Multi-Model Quiz Generation - Build Script"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "Checking dependencies..."
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command_exists node; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Accept choice as command-line argument or prompt for it
if [ -n "$1" ]; then
    choice="$1"
else
    echo "Select build option:"
    echo "1) Build without Docker (local development)"
    echo "2) Build with Docker"
    read -p "Enter choice (1 or 2): " choice
fi

if [ "$choice" = "1" ]; then
    echo "Building without Docker..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "Running backend tests..."
    pytest tests/ -v
    
    cd ..
    
    # Frontend setup
    echo "Setting up frontend..."
    cd frontend
    npm install
    npm test -- --watchAll=false
    npm run build
    
    cd ..
    
    echo "Build completed successfully!"
    echo "To start services:"
    echo "  Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "  Frontend: cd frontend && npm start"
    
elif [ "$choice" = "2" ]; then
    echo "Building with Docker..."
    
    # Create Dockerfile for backend
    cat > Dockerfile.backend << 'DOCKER_EOF'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKER_EOF

    # Create Dockerfile for frontend
    cat > Dockerfile.frontend << 'DOCKER_EOF'
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

RUN npm run build

RUN npm install -g serve

CMD ["serve", "-s", "build", "-l", "3000"]
DOCKER_EOF

    # Create docker-compose.yml
    cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://quizuser:quizpass@postgres:5432/quizdb
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY:-}
    depends_on:
      - postgres
      - redis
    networks:
      - quiz-network

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
    networks:
      - quiz-network

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=quizuser
      - POSTGRES_PASSWORD=quizpass
      - POSTGRES_DB=quizdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - quiz-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - quiz-network

volumes:
  postgres_data:

networks:
  quiz-network:
    driver: bridge
COMPOSE_EOF

    echo "Building Docker images..."
    docker-compose build
    
    echo "Build completed successfully!"
    echo "To start services: docker-compose up"
    
else
    echo "Invalid choice"
    exit 1
fi
