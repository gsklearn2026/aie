#!/bin/bash

echo "🎬 AI Quiz Platform - Docker Compose Demo"
echo "=========================================="

echo "📊 Checking all services status..."
docker-compose ps

echo ""
echo "🏥 Health Check Results:"
curl -s http://localhost:8000/health | python -m json.tool

echo ""
echo "📚 Available Quizzes:"
curl -s http://localhost:8000/api/quizzes | python -m json.tool

echo ""
echo "📈 Platform Statistics:"
curl -s http://localhost:8000/api/stats | python -m json.tool

echo ""
echo "🧪 Testing AI Question Generation..."
curl -s -X POST http://localhost:8000/api/generate-question \
  -H "Content-Type: application/json" \
  -d '{"topic":"Docker Compose","difficulty":"medium"}' | python -m json.tool

echo ""
echo "✨ Demo Complete!"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo "🔧 API Documentation: http://localhost:8000/health"
echo "📊 Service Monitoring: docker-compose logs -f"
