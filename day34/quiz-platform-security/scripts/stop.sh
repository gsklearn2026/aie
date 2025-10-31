#!/bin/bash

echo "🛑 Stopping Quiz Platform Security Testing Environment..."

# Stop Docker services
cd docker
docker-compose down

echo "🧹 Cleaning up containers and networks..."
docker-compose down --volumes --remove-orphans

echo "✅ All services stopped and cleaned up!"
