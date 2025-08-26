#!/bin/bash

echo "🛑 Stopping Topic Relationship Mapping Service..."

# Stop Node and Python processes
pkill -f "npm start" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null

# Stop Docker services
cd docker
docker-compose down

echo "✅ Services stopped"
