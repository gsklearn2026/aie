#!/bin/bash

echo "🛑 Stopping AI Quiz Platform"
echo "============================="

if docker-compose ps >/dev/null 2>&1; then
    echo "🐳 Stopping Docker Compose services..."
    docker-compose down
    
    if [[ "$1" == "--clean" ]]; then
        echo "🧹 Cleaning up volumes and images..."
        docker-compose down -v --rmi all
        docker system prune -f
    fi
    
    echo "✅ Docker services stopped!"
else
    echo "🏠 Stopping local development servers..."
    
    # Kill backend processes
    pkill -f "python app.py" || true
    pkill -f "flask run" || true
    
    # Kill frontend processes
    pkill -f "npm start" || true
    pkill -f "react-scripts start" || true
    
    echo "✅ Local servers stopped!"
fi
