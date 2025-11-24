#!/bin/bash

echo "======================================"
echo "Running Documentation System Tests"
echo "======================================"

cd backend
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

echo "Running pytest..."
python -m pytest tests/ -v --tb=short

echo ""
echo "======================================"
echo "Test Results Summary"
echo "======================================"
