#!/bin/bash

echo "🛑 Stopping AI Quiz Platform..."

# Kill backend
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

# Kill frontend
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
fi

# Stop Redis
redis-cli shutdown 2>/dev/null

echo "✅ All services stopped"
