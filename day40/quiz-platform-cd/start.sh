#!/bin/bash

echo "🚀 Starting Quiz Platform CD Pipeline Demo"
echo "=========================================="

# Check if services are already running
if docker ps | grep -q quiz-backend; then
    echo "⚠️  Services already running. Stopping first..."
    ./stop.sh
fi

# Start services
echo "🟢 Starting services..."
docker run -d \
    --name quiz-backend-staging \
    -p 8001:8000 \
    -e ENVIRONMENT=staging \
    -e GEMINI_API_KEY=${GEMINI_API_KEY:-"demo-key"} \
    quiz-platform-backend:latest

docker run -d \
    --name quiz-backend-production \
    -p 8002:8000 \
    -e ENVIRONMENT=production \
    -e GEMINI_API_KEY=${GEMINI_API_KEY:-"demo-key"} \
    quiz-platform-backend:latest

echo "⏳ Waiting for services to start..."
sleep 10

echo "✅ Services started successfully!"
echo ""
echo "🌐 Available endpoints:"
echo "   Staging:    http://localhost:8001"
echo "   Production: http://localhost:8002"
echo ""
echo "🧪 Quick health check:"
curl -s http://localhost:8001/health | grep -o '"status":"[^"]*"' || echo "❌ Staging not responding"
curl -s http://localhost:8002/health | grep -o '"status":"[^"]*"' || echo "❌ Production not responding"
