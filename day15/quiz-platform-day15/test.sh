#!/bin/bash

echo "🧪 Running tests for Question Difficulty Classification"

# Backend tests
echo "🔬 Running backend tests..."
cd backend
python -m pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo "✅ Backend tests passed!"
else
    echo "❌ Backend tests failed!"
    exit 1
fi

cd ..

# Frontend tests (basic)
echo "🎨 Running frontend tests..."
cd frontend
npm test -- --run --watchAll=false

if [ $? -eq 0 ]; then
    echo "✅ Frontend tests passed!"
else
    echo "❌ Frontend tests failed!"
    exit 1
fi

cd ..

echo "🎉 All tests completed successfully!"
