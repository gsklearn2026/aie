#!/bin/bash

echo "🧪 Running tests..."

# Unit tests
echo "Running unit tests..."
cd tests/unit
python3 test_memory_tracker.py
cd ../..

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Integration tests
echo "Running integration tests..."
cd tests/integration
python3 test_api.py
cd ../..

echo "✅ All tests completed!"
