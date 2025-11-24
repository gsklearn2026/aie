#!/bin/bash

echo "Running post-deployment verification..."

# Check health endpoints
echo "1. Checking health endpoints..."
curl -f http://localhost/api/health || { echo "Health check failed!"; exit 1; }
curl -f http://localhost/api/health/ready || { echo "Readiness check failed!"; exit 1; }

# Test authentication
echo "2. Testing authentication..."
TOKEN=$(curl -s -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"test123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Authentication failed!"
    exit 1
fi

# Test quiz generation
echo "3. Testing quiz generation..."
curl -f -X POST http://localhost/api/quiz/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python","difficulty":"medium","num_questions":3}' || { echo "Quiz generation failed!"; exit 1; }

# Test leaderboard
echo "4. Testing leaderboard..."
curl -f http://localhost/api/leaderboard/ || { echo "Leaderboard failed!"; exit 1; }

echo "All verification tests passed!"
