#!/bin/bash

echo "🛑 Stopping all services..."

# Kill backend and frontend
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true

# Stop Docker services
docker-compose down 2>/dev/null || true

echo "✅ All services stopped"
