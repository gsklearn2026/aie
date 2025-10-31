#!/bin/bash

echo "🛑 Stopping Day 33 Load Testing and Performance Monitoring"

if [ -f ".dashboard.pid" ] && [ -f ".locust.pid" ]; then
    echo "🐍 Stopping local services..."
    
    # Stop dashboard
    if [ -f ".dashboard.pid" ]; then
        DASHBOARD_PID=$(cat .dashboard.pid)
        kill $DASHBOARD_PID 2>/dev/null
        rm .dashboard.pid
        echo "📊 Performance dashboard stopped"
    fi
    
    # Stop Locust
    if [ -f ".locust.pid" ]; then
        LOCUST_PID=$(cat .locust.pid)
        kill $LOCUST_PID 2>/dev/null
        rm .locust.pid
        echo "🔥 Locust stopped"
    fi
    
    # Stop Redis if we started it
    pkill redis-server
    echo "🔴 Redis stopped"

elif [ -f "docker/docker-compose.yml" ]; then
    echo "🐳 Stopping Docker services..."
    cd docker
    docker-compose down
    echo "✅ Docker services stopped"
    cd ..
else
    echo "ℹ️  No running services found"
fi

echo "✅ All services stopped!"
