#!/bin/bash

echo "========================================"
echo "Running Tests"
echo "========================================"

cd backend
source venv/bin/activate

echo "Running integration tests..."
pytest ../tests/integration/ -v

echo ""
echo "To run load tests:"
echo "  locust -f tests/load/locustfile.py --host=http://localhost:8000"
