#!/bin/bash

echo "🛑 Stopping Quiz Export Service..."

# Kill backend processes
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null
    rm .backend.pid
fi

if [ -f .celery.pid ]; then
    kill $(cat .celery.pid) 2>/dev/null
    rm .celery.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null
    rm .frontend.pid
fi

# Stop Docker services
docker-compose down

echo "✅ All services stopped successfully!"
