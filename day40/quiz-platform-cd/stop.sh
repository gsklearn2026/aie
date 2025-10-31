#!/bin/bash

echo "🛑 Stopping Quiz Platform services..."

# Stop and remove containers
docker stop quiz-backend-staging quiz-backend-production quiz-backend-green quiz-backend-blue 2>/dev/null || true
docker rm quiz-backend-staging quiz-backend-production quiz-backend-green quiz-backend-blue 2>/dev/null || true

echo "✅ All services stopped"
