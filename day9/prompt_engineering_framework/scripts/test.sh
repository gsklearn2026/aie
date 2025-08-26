#!/bin/bash
# Run all tests

echo "Running tests..."

# Run pytest with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo "Tests complete! Coverage report available in htmlcov/"
