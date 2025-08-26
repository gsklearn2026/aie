#!/bin/bash

echo "🎬 Running Error Handling Framework Demo"

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Testing API endpoints..."

# Test health endpoint
echo "Testing health endpoint..."
curl -s http://localhost:8000/api/quiz/health | jq .

# Test quiz generation with valid input
echo "Testing quiz generation (valid)..."
curl -s -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python", "difficulty": "medium", "count": 3}' | jq .

# Test quiz generation with invalid input (should trigger validation error)
echo "Testing validation error handling..."
curl -s -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "", "difficulty": "medium", "count": 25}' | jq .

# Test non-existent endpoint (should trigger 404 handling)
echo "Testing 404 error handling..."
curl -s http://localhost:8000/api/nonexistent | jq .

echo "✅ Demo completed! Check the responses above to see error handling in action."
echo "🌐 Visit http://localhost:3000 to see the full UI"
