#!/bin/bash

# Content Verification Service Demo Script
# This script starts Redis, the service, and runs the demo

set -e

echo "🚀 Starting Content Verification Service Demo"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Redis is already running
if docker ps | grep -q redis; then
    print_warning "Redis container is already running"
    REDIS_CONTAINER=$(docker ps --filter "ancestor=redis:7-alpine" --format "{{.Names}}")
else
    print_status "Starting Redis container..."
    REDIS_CONTAINER=$(docker run -d -p 6379:6379 --name content-verification-redis redis:7-alpine)
    print_success "Redis container started: $REDIS_CONTAINER"
fi

# Wait for Redis to be ready
print_status "Waiting for Redis to be ready..."
sleep 3

npm install
# Check if service is already running
if pgrep -f "node src/server.js" > /dev/null; then
    print_warning "Content Verification Service is already running"
else
    print_status "Starting Content Verification Service..."
    npm start &
    SERVICE_PID=$!
    echo $SERVICE_PID > .service.pid
    
    # Wait for service to start
    print_status "Waiting for service to start..."
    sleep 5
    
    # Check if service started successfully
    if curl -s http://localhost:3003/api/verification/health > /dev/null; then
        print_success "Content Verification Service started successfully"
    else
        print_error "Failed to start Content Verification Service"
        exit 1
    fi
fi

echo ""
echo "🎯 Service Status:"
echo "=================="
echo "✅ Redis: Running on port 6379"
echo "✅ API: Running on http://localhost:3003"
echo "✅ Health Check: http://localhost:3003/api/verification/health"
echo ""

# Check if .env has a real API key
if grep -q "your_anthropic_api_key_here" .env; then
    print_warning "Using placeholder API key. Claude AI features will not work."
    print_warning "Add your real Anthropic API key to .env file for full functionality."
    echo ""
fi

# Run the demo
print_status "Running demo..."
echo ""

# Run the demo script
node demo.js

echo ""
echo "🎉 Demo completed!"
echo ""
echo "📋 Available endpoints:"
echo "   GET  /api/verification/health     - Health check"
echo "   POST /api/verification/verify     - Synchronous verification"
echo "   POST /api/verification/verify/async - Asynchronous verification"
echo "   POST /api/verification/verify/batch - Batch verification"
echo "   GET  /api/verification/job/:jobId - Job status"
echo ""
echo "🌐 Interactive Demo: Open demo.html in your browser"
echo "🛑 To stop everything: ./cleanup.sh"
echo "" 