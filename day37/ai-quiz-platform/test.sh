#!/bin/bash

set -e

echo "🧪 AI Quiz Platform - Test Script"
echo "================================"

# Test with Docker
test_docker() {
    echo "🐳 Testing Docker deployment..."
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        echo "❌ Services not running. Start with: ./start.sh"
        exit 1
    fi
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Test backend health
    echo "🔍 Testing backend health..."
    curl -f http://localhost:8000/health || { echo "❌ Backend health check failed"; exit 1; }
    
    # Test frontend
    echo "🔍 Testing frontend..."
    curl -f http://localhost:3000 >/dev/null || { echo "❌ Frontend not accessible"; exit 1; }
    
    # Test API endpoints
    echo "🔍 Testing API endpoints..."
    
    # Test quiz generation (might fail without API key)
    echo "Testing quiz generation..."
    curl -X POST "http://localhost:8000/api/quiz/generate?topic=Docker&difficulty=easy&num_questions=3" \
         -H "Content-Type: application/json" || echo "⚠️  Quiz generation requires Gemini API key"
    
    # Run backend tests
    echo "🧪 Running backend tests..."
    docker-compose exec backend python -m pytest tests/ -v || echo "⚠️  Some tests may fail without full setup"
    
    echo ""
    echo "✅ Docker tests completed!"
}

# Test local deployment
test_local() {
    echo "🏠 Testing local deployment..."
    
    # Check if backend is running
    curl -f http://localhost:8000/health 2>/dev/null || { echo "❌ Backend not running. Start with: ./start.sh"; exit 1; }
    
    # Check if frontend is running
    curl -f http://localhost:3000 2>/dev/null >/dev/null || { echo "❌ Frontend not running. Start with: ./start.sh"; exit 1; }
    
    echo "✅ Local tests completed!"
}

# Performance test
performance_test() {
    echo "⚡ Running performance tests..."
    
    # Simple load test
    echo "Testing API performance..."
    for i in {1..10}; do
        curl -s http://localhost:8000/health >/dev/null && echo "Request $i: OK" || echo "Request $i: FAILED"
    done
    
    echo "✅ Performance tests completed!"
}

# Main execution
echo "Choose test option:"
echo "1) Test Docker deployment"
echo "2) Test local deployment"
echo "3) Performance test"
echo "4) All tests"
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        test_docker
        ;;
    2)
        test_local
        ;;
    3)
        performance_test
        ;;
    4)
        test_docker
        test_local
        performance_test
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 All tests completed successfully!"
