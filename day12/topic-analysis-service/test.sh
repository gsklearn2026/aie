#!/bin/bash
set -e

echo "🧪 Running Topic Analysis Service Tests"
echo "======================================="

# Run unit tests
echo "Running unit tests..."
python3 -m pytest tests/ -v --tb=short

# Run integration tests
echo "Running integration tests..."
python3 -m pytest tests/ -v --tb=short -m "not slow"

echo "✅ All tests passed!"
