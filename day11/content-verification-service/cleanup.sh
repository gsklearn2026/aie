#!/bin/bash

# Content Verification Service Cleanup Script
# This script stops the service, Redis, and cleans up resources

set -e

echo "🧹 Cleaning up Content Verification Service"
echo "==========================================="

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

# Stop Content Verification Service
print_status "Stopping Content Verification Service..."

# Kill service if running
if pgrep -f "node src/server.js" > /dev/null; then
    pkill -f "node src/server.js"
    print_success "Content Verification Service stopped"
else
    print_warning "Content Verification Service was not running"
fi

# Remove PID file if it exists
if [ -f .service.pid ]; then
    rm .service.pid
    print_success "Removed service PID file"
fi

# Stop Redis container
print_status "Stopping Redis container..."

if docker ps | grep -q content-verification-redis; then
    docker stop content-verification-redis
    docker rm content-verification-redis
    print_success "Redis container stopped and removed"
elif docker ps | grep -q redis; then
    print_warning "Found Redis container but not the expected one"
    print_warning "You may need to manually stop Redis containers"
else
    print_warning "No Redis container found"
fi

# Clean up any orphaned containers
print_status "Cleaning up orphaned containers..."
docker container prune -f > /dev/null 2>&1 || true

# Clean up any dangling images (optional)
read -p "Do you want to clean up dangling Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleaning up dangling Docker images..."
    docker image prune -f > /dev/null 2>&1 || true
    print_success "Docker images cleaned up"
fi

# Clean up node_modules (optional)
read -p "Do you want to remove node_modules to free up space? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing node_modules..."
    rm -rf node_modules
    print_success "node_modules removed"
    print_warning "Run 'npm install' to reinstall dependencies"
fi

# Clean up logs (optional)
read -p "Do you want to clean up log files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleaning up log files..."
    find . -name "*.log" -delete 2>/dev/null || true
    print_success "Log files cleaned up"
fi

echo ""
print_success "Cleanup completed!"
echo ""
echo "📋 What was cleaned up:"
echo "   ✅ Content Verification Service (stopped)"
echo "   ✅ Redis container (stopped and removed)"
echo "   ✅ Service PID file (removed)"
echo "   ✅ Orphaned Docker containers (cleaned)"
echo ""
echo "🚀 To start again: ./demo.sh"
echo "" 