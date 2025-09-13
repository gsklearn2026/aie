#!/bin/bash

echo "🚀 Starting Day 33 Load Testing and Performance Monitoring"

# Check build option
if [ -d "venv" ]; then
    echo "🐍 Starting local Python environment..."
    source venv/bin/activate
    
    # Start Redis (if not running)
    if ! pgrep -x "redis-server" > /dev/null; then
        echo "🔴 Starting Redis server..."
        redis-server --daemonize yes
    fi
    
    # Start performance dashboard
    echo "📊 Starting performance dashboard..."
    streamlit run src/performance_monitor/dashboard.py --server.port 8081 &
    DASHBOARD_PID=$!
    
    # Start Locust web interface
    echo "🔥 Starting Locust web interface..."
    locust -f src/load_tests/quiz_platform_load_test.py --host=http://localhost:8000 --web-port 8090 &
    LOCUST_PID=$!
    
    echo "✅ Services started!"
    echo "📊 Performance Dashboard: http://localhost:8081"
    echo "🔥 Locust Web UI: http://localhost:8090"
    echo "📝 Log files in: ./reports/"
    
    # Save PIDs for cleanup
    echo $DASHBOARD_PID > .dashboard.pid
    echo $LOCUST_PID > .locust.pid

elif [ -f "docker/docker-compose.yml" ]; then
    echo "🐳 Starting Docker environment..."
    
    cd docker
    docker-compose up -d
    
    echo "✅ Docker services started!"
    echo "📊 Performance Dashboard: http://localhost:8081"
    echo "🔥 Locust Web UI: http://localhost:8090" 
    echo "🐳 View logs: docker-compose logs -f"
    
    cd ..
else
    echo "❌ No build environment found. Please run './build.sh' first."
    exit 1
fi

echo ""
echo "🎯 Load Testing Quick Start:"
echo "1. Open Performance Dashboard: http://localhost:8081"
echo "2. Open Locust UI: http://localhost:8090"
echo "3. Configure test parameters and start load testing"
echo "4. Monitor results in real-time dashboard"

# Run demo load test
echo ""
read -p "🚀 Run demo load test now? (y/n): " run_demo

if [ "$run_demo" == "y" ]; then
    echo "🔥 Running demo load test..."
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Run baseline test
    locust -f src/load_tests/quiz_platform_load_test.py --headless \
           -u 5 -r 1 -t 30s --host=http://localhost:8000 \
           --html reports/demo_test_report.html
    
    echo "✅ Demo test complete! Check reports/demo_test_report.html"
    
    # Run performance analysis
    python src/utils/performance_analyzer.py
    
    echo "📈 Analysis complete! Check reports/performance_analysis.txt"
fi
