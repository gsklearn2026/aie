#!/bin/bash

echo "🧪 Running Error Handling Framework Tests"

# Backend tests
echo "🐍 Running Backend Tests..."
cd backend
source ../venv/bin/activate
export PYTHONPATH=.
python -m pytest src/tests/ -v
cd ..

# Frontend tests
echo "⚛️  Running Frontend Tests..."
cd frontend
npm test -- --watchAll=false
cd ..

echo "✅ All tests completed!"
