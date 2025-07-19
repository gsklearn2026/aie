#!/bin/bash

echo "🎭 Starting Question Difficulty Classification Demo"

# Check if services are running
echo "🔍 Checking backend service..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running. Starting backend..."
    cd backend
    python -m uvicorn app.main:app --reload &
    BACKEND_PID=$!
    cd ..
    sleep 5
fi

echo "🔍 Checking frontend service..."
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend not running. Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    sleep 10
fi

echo "🎯 Testing classification API..."

# Test easy question
echo "Testing beginner question..."
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is 2 + 2?",
    "subject": "mathematics", 
    "question_type": "multiple_choice"
  }' | jq '.'

echo ""

# Test hard question  
echo "Testing expert question..."
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Analyze the implications of Heisenberg uncertainty principle on the philosophical concept of determinism in quantum mechanics and its relationship to classical physics paradigms.",
    "subject": "physics",
    "question_type": "essay"
  }' | jq '.'

echo ""
echo "🎉 Demo completed!"
echo "📊 Open http://localhost:3000 to use the web interface"
echo "📚 API docs available at http://localhost:8000/docs"

# Cleanup background processes on exit
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT
