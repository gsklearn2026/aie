#!/bin/bash
# Build script for question generation service

set -e

echo "🔨 Building Question Generation Service..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Code formatting
echo "🎨 Formatting code..."
black src/ tests/
isort src/ tests/

# Type checking
echo "🔍 Type checking..."
mypy src/

# Lint
echo "🧹 Linting..."
flake8 src/ tests/ --max-line-length=88 --ignore=E203,W503

echo "✅ Build completed successfully!"
