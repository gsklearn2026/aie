#!/bin/bash

echo "🛑 AI Quiz Platform - Stop Script"
echo "================================"

# Function to show menu
show_menu() {
    echo ""
    echo "Choose stop option:"
    echo "1) Stop Docker containers"
    echo "2) Stop local processes"
    echo "3) Clean everything (Docker)"
    echo "4) Exit"
    read -p "Enter your choice (1-4): " choice
}

# Stop Docker containers
stop_docker() {
    echo "🐳 Stopping Docker containers..."
    docker-compose down
    echo "✅ Docker containers stopped"
}

# Stop local processes
stop_local() {
    echo "🏠 Stopping local processes..."
    pkill -f "uvicorn app.main:app" || echo "No backend process found"
    pkill -f "npm start" || echo "No frontend process found"
    pkill -f "node.*react-scripts" || echo "No React process found"
    echo "✅ Local processes stopped"
}

# Clean everything
clean_docker() {
    echo "🧹 Cleaning Docker environment..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo "✅ Docker environment cleaned"
}

# Main execution
show_menu

case $choice in
    1)
        stop_docker
        ;;
    2)
        stop_local
        ;;
    3)
        clean_docker
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
