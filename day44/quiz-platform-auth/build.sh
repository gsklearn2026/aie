#!/bin/bash

echo "🚀 Building AI Quiz Platform Authentication System..."

# Function to show usage
show_usage() {
    echo "Usage: $0 [--docker|--local]"
    echo "  --docker: Build and run with Docker"
    echo "  --local: Build and run locally"
    exit 1
}

# Parse arguments
BUILD_MODE="local"
if [ "$1" = "--docker" ]; then
    BUILD_MODE="docker"
elif [ "$1" = "--local" ] || [ -z "$1" ]; then
    BUILD_MODE="local"
else
    show_usage
fi

echo "Build mode: $BUILD_MODE"

if [ "$BUILD_MODE" = "docker" ]; then
    echo "🐳 Docker build mode selected"
    
    # Create Dockerfile for backend
    cat > backend/Dockerfile << 'DOCKERFILE_EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
DOCKERFILE_EOF

    # Create Dockerfile for frontend
    cat > frontend/Dockerfile << 'DOCKERFILE_EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
DOCKERFILE_EOF

    # Create docker-compose.yml
    cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-super-secret-key-change-in-production
      - DATABASE_URL=sqlite:///./quiz_platform.db
      - GEMINI_API_KEY=your-gemini-api-key-here
    volumes:
      - ./backend:/app
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

COMPOSE_EOF

    echo "📦 Building Docker containers..."
    docker-compose build

    echo "🏃‍♂️ Starting services with Docker..."
    docker-compose up -d

    echo "✅ Docker deployment complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"

else
    echo "🏠 Local build mode selected"
    
    # Setup Python virtual environment
    echo "🐍 Setting up Python virtual environment..."
    cd backend
    python -m venv venv
    
    # Activate virtual environment and install dependencies
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Backend dependencies installed"
    
    # Setup Node.js environment
    echo "📦 Setting up Node.js environment..."
    cd ../frontend
    npm install
    
    echo "✅ Frontend dependencies installed"
    
    # Run tests
    echo "🧪 Running backend tests..."
    cd ../backend
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    python -m pytest tests/ -v
    
    echo "✅ Tests completed"
    
    # Start services
    echo "🏃‍♂️ Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    echo "🏃‍♂️ Starting frontend server..."
    cd ../frontend
    npm start &
    FRONTEND_PID=$!
    
    echo "⏳ Waiting for frontend to start..."
    sleep 10
    
    echo "✅ Local deployment complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "🛑 To stop services:"
    echo "  Backend PID: $BACKEND_PID"
    echo "  Frontend PID: $FRONTEND_PID"
    echo "  Or run: ./stop.sh"
    
    # Save PIDs for stop script
    echo $BACKEND_PID > backend.pid
    echo $FRONTEND_PID > frontend.pid
fi

echo ""
echo "🎉 Authentication system is ready!"
echo ""
echo "📋 Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Create Account' to register a new user"
echo "3. Login with your credentials"
echo "4. Test the protected dashboard features"
echo "5. Check the API documentation at http://localhost:8000/docs"
