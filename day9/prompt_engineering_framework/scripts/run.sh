#!/bin/bash
# Run the application

echo "Starting Prompt Engineering Framework..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./scripts/setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run application
python main.py
