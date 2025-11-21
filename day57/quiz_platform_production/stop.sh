#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=== Stopping Quiz Platform ==="

if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
    echo "Stopping local services..."
    kill $(cat "$PROJECT_ROOT/.backend.pid") 2>/dev/null || true
    kill $(cat "$PROJECT_ROOT/.frontend.pid") 2>/dev/null || true
    rm -f "$PROJECT_ROOT/.backend.pid" "$PROJECT_ROOT/.frontend.pid"
    echo "Local services stopped"
else
    echo "Stopping Docker services..."
    cd "$PROJECT_ROOT"
    docker-compose down
    echo "Docker services stopped"
fi
