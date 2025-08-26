#!/bin/bash
set -e

echo "🎯 Topic Analysis Service Demo"
echo "==============================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Service is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - Service not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Service failed to start within expected time"
    return 1
}

# Function to kill existing processes
cleanup() {
    echo "🧹 Cleaning up existing processes..."
    pkill -f "uvicorn main:app" 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
}

# Step 1: Install dependencies
echo "📦 Step 1: Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Step 2: Build the project
echo "🏗️ Step 2: Building the project..."
if [ -f "build.sh" ]; then
    ./build.sh
    echo "✅ Build completed"
else
    echo "⚠️ build.sh not found, skipping build step"
fi

# Step 3: Check and start Redis
echo "🔴 Step 3: Checking Redis..."
if command_exists redis-cli; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "⚠️ Redis not running, attempting to start..."
        redis-server --daemonize yes 2>/dev/null || echo "⚠️ Could not start Redis, continuing anyway..."
    fi
else
    echo "⚠️ Redis CLI not found, assuming Redis is running or not needed"
fi

# Step 4: Clean up any existing processes
cleanup

# Step 5: Start the service
echo "🚀 Step 4: Starting the service..."
cd src
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVICE_PID=$!
cd ..

# Step 6: Wait for service to be ready
if wait_for_service; then
    echo "✅ Service started successfully"
else
    echo "❌ Failed to start service"
    kill $SERVICE_PID 2>/dev/null || true
    exit 1
fi

# Step 7: Run the demo tests
echo "🧪 Step 5: Running demo tests..."

# Test health endpoint
echo "🔍 Testing health endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool

# Test topic analysis
echo -e "\n🧠 Testing topic analysis..."
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience. Deep learning, a specialized area within machine learning, uses neural networks with multiple layers to model and understand complex patterns in data.",
    "options": {
      "max_topics": 5,
      "confidence_threshold": 0.6,
      "include_subtopics": true,
      "extract_concepts": true
    }
  }' | python3 -m json.tool

# Test cache stats
echo -e "\n📊 Testing cache statistics..."
curl -s http://localhost:8000/cache/stats | python3 -m json.tool

echo -e "\n🎉 Demo completed successfully!"
echo "🌐 Visit http://localhost:8000 for the web interface"
echo "📈 Visit http://localhost:8000/metrics for Prometheus metrics"
echo ""
echo "Press Ctrl+C to stop the service"

# Keep the service running and handle cleanup on exit
trap 'echo -e "\n🛑 Stopping service..."; kill $SERVICE_PID 2>/dev/null || true; cleanup; echo "✅ Service stopped"; exit 0' INT TERM

# Wait for the service process
wait $SERVICE_PID
