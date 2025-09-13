#!/bin/bash

echo "🔨 Building Day 33 Load Testing and Performance Monitoring"

# Option selection
echo "Choose build option:"
echo "1) Local Python environment"
echo "2) Docker environment"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🐍 Setting up local Python environment..."
        
        # Create virtual environment
        python3 -m venv venv
        source venv/bin/activate
        
        # Install dependencies
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create reports directory
        mkdir -p reports
        
        # Initialize performance metrics log
        echo "timestamp,users,rps,failures,avg_response_time" > reports/performance_metrics.log
        
        echo "✅ Local environment ready!"
        echo "📁 Project structure created"
        echo "📦 Dependencies installed"
        echo "📊 Monitoring dashboard available"
        
        ;;
    2)
        echo "🐳 Setting up Docker environment..."
        
        # Build Docker images
        cd docker
        docker-compose build
        
        # Create reports directory
        mkdir -p ../reports
        
        echo "✅ Docker environment ready!"
        echo "🐳 Docker images built"
        echo "📂 Project structure created"
        
        cd ..
        ;;
    *)
        echo "❌ Invalid choice. Please run again and select 1 or 2."
        exit 1
        ;;
esac

# Run tests
echo "🧪 Running tests..."

if [ "$choice" == "1" ]; then
    source venv/bin/activate
fi

python -m pytest tests/ -v

echo "✅ Build complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run './start.sh' to start the performance monitoring dashboard"
echo "2. Execute load tests using the dashboard or command line"
echo "3. View results in the monitoring dashboard at http://localhost:8080"
