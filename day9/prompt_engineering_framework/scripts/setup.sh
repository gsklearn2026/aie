#!/bin/bash
# Setup development environment

echo "Setting up Prompt Engineering Framework..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs

# Copy environment file
cp .env.example .env

echo "Setup complete! Activate environment with: source venv/bin/activate"
