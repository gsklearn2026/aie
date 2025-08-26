#!/bin/bash

echo "🎯 Running Logging and Monitoring Demo"

# Wait for services to be ready
sleep 3

echo "📝 Submitting test quiz answers..."

# Submit multiple test quiz answers
curl -X POST http://localhost:8080/api/v1/quiz/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: demo_user_1" \
  -H "X-Session-ID: session_123" \
  -d '{
    "question_id": "q1",
    "quiz_type": "math",
    "question": "What is 2 + 2?",
    "answer": "4"
  }'

curl -X POST http://localhost:8080/api/v1/quiz/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: demo_user_2" \
  -H "X-Session-ID: session_456" \
  -d '{
    "question_id": "q2",
    "quiz_type": "science",
    "question": "What is the capital of France?",
    "answer": "Paris"
  }'

echo "📊 Fetching metrics..."
curl -s http://localhost:8080/api/v1/metrics/summary | jq '.'

echo "🔍 Searching logs..."
curl -s "http://localhost:8080/api/v1/logs/search?query=quiz_submission" | jq '.logs | length'

echo "✅ Demo completed! Check the dashboard at http://localhost:3000"
