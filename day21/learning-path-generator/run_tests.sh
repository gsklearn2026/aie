#!/bin/bash

echo "🧪 Running Learning Path Generator Tests"
echo "========================================"

# Activate virtual environment
source venv/bin/activate

# Run backend tests
echo "🐍 Running backend tests..."
cd backend
python -m pytest tests/ -v --tb=short
TEST_RESULT=$?
cd ..

# Run frontend tests (if they exist)
echo "⚛️  Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi
