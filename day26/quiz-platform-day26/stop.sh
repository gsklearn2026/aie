#!/bin/bash

echo "🛑 Stopping Quiz Platform services..."

# Kill processes if PID file exists
if [ -f .pids ]; then
    PIDS=$(cat .pids)
    for PID in $PIDS; do
        if ps -p $PID > /dev/null; then
            echo "Stopping process $PID..."
            kill $PID
        fi
    done
    rm .pids
fi

# Stop Docker services
echo "🐳 Stopping Docker services..."
cd docker
docker-compose down

echo "✅ All services stopped!"
