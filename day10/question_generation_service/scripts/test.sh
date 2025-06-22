#!/bin/bash
# Test script for question generation service

set -e

echo "🧪 Running tests..."

# Unit tests
echo "🔬 Running unit tests..."
pytest tests/unit/ -v --cov=src/question_service --cov-report=term-missing

# Integration tests
echo "🔗 Running integration tests..."
pytest tests/integration/ -v

# E2E tests
echo "🌐 Running E2E tests..."
pytest tests/e2e/ -v

echo "✅ All tests passed!"
