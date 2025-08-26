#!/bin/bash
# Deployment script

set -e

MODE=${1:-local}

echo "🚀 Deploying in $MODE mode..."

if [ "$MODE" = "docker" ]; then
    echo "🐳 Building Docker image..."
    docker build -t question-service .
    
    echo "🐳 Starting services with Docker Compose..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "🔍 Checking service health..."
    curl -f http://localhost:8000/health || exit 1
    
else
    echo "🏃 Starting Redis..."
    redis-server --daemonize yes
    
    echo "🗄️ Starting PostgreSQL..."
    # Note: Assumes PostgreSQL is already installed and configured
    
    echo "🌐 Starting application..."
    uvicorn src.question_service.api.main:app --host 0.0.0.0 --port 8000 --reload &
    
    # Set environment for Anthropic
    export AI_PROVIDER=anthropic
    export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-"your-anthropic-api-key-here"}
    
    echo "⏳ Waiting for application to start..."
    sleep 5
    
    echo "🔍 Checking application health..."
    curl -f http://localhost:8000/health || exit 1
fi

echo "✅ Deployment completed successfully!"
