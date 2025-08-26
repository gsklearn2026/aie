#!/bin/bash

echo "🛑 Stopping Performance Analytics Engine..."

# Kill backend and frontend processes
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
fi

# Stop Docker services
docker-compose down

echo "✅ Performance Analytics Engine stopped."
