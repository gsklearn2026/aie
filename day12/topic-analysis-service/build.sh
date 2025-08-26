#!/bin/bash
set -e

echo "🏗️ Building Topic Analysis Service"
echo "================================="

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build completed successfully!"
