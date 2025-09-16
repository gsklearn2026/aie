#!/bin/bash

echo "🧪 Running Security Testing Suite..."

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements/base.txt
    cd ..
fi

# Activate virtual environment
cd backend
source venv/bin/activate

# Run tests
echo "🔬 Running unit tests..."
python -m pytest tests/ -v --tb=short

# Run security tests
echo "🔒 Running security tests..."
python -m pytest tests/test_security.py -v --tb=short

# Run linting
echo "🔍 Running code quality checks..."
python -m flake8 src/ --max-line-length=100
python -m black --check src/
python -m isort --check-only src/

echo "✅ All tests completed!"
