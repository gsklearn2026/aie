#!/bin/bash

# Progressive Difficulty System - Stop Script
# This script stops all services and cleans up resources

set -e  # Exit on any error

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

# Function to stop Docker services
stop_docker() {
    print_status "Stopping Docker services..."
    
    # Stop all services
    docker-compose down
    
    # Remove any dangling containers
    docker container prune -f > /dev/null 2>&1 || true
    
    # Remove any dangling images
    docker image prune -f > /dev/null 2>&1 || true
    
    print_success "Docker services stopped"
}

# Function to stop local services
stop_local() {
    print_status "Stopping local services..."
    
    # Stop backend if PID file exists
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            print_status "Stopping Backend (PID: $BACKEND_PID)..."
            kill $BACKEND_PID 2>/dev/null || true
            sleep 2
            # Force kill if still running
            if ps -p $BACKEND_PID > /dev/null 2>&1; then
                kill -9 $BACKEND_PID 2>/dev/null || true
            fi
            print_success "Backend stopped"
        else
            print_warning "Backend process not found"
        fi
        rm -f .backend.pid
    else
        print_warning "Backend PID file not found"
    fi
    
    # Stop frontend if PID file exists
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            print_status "Stopping Frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID 2>/dev/null || true
            sleep 2
            # Force kill if still running
            if ps -p $FRONTEND_PID > /dev/null 2>&1; then
                kill -9 $FRONTEND_PID 2>/dev/null || true
            fi
            print_success "Frontend stopped"
        else
            print_warning "Frontend process not found"
        fi
        rm -f .frontend.pid
    else
        print_warning "Frontend PID file not found"
    fi
    
    # Kill any remaining processes on our ports
    print_status "Cleaning up port usage..."
    
    # Kill processes on port 3000 (frontend)
    FRONTEND_PROCESSES=$(lsof -ti:3000 2>/dev/null || true)
    if [ ! -z "$FRONTEND_PROCESSES" ]; then
        print_status "Killing processes on port 3000..."
        echo $FRONTEND_PROCESSES | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill processes on port 8000 (backend)
    BACKEND_PROCESSES=$(lsof -ti:8000 2>/dev/null || true)
    if [ ! -z "$BACKEND_PROCESSES" ]; then
        print_status "Killing processes on port 8000..."
        echo $BACKEND_PROCESSES | xargs kill -9 2>/dev/null || true
    fi
    
    print_success "Local services stopped"
}

# Function to check if services are running
check_services() {
    local running_services=()
    
    # Check if Docker services are running
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        if docker-compose ps | grep -q "Up"; then
            running_services+=("Docker")
        fi
    fi
    
    # Check if local services are running
    if [ -f ".backend.pid" ] || [ -f ".frontend.pid" ]; then
        running_services+=("Local")
    fi
    
    # Check if processes are running on our ports
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 || lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        if [[ ! " ${running_services[@]} " =~ " Local " ]]; then
            running_services+=("Local")
        fi
    fi
    
    echo "${running_services[@]}"
}

# Function to cleanup temporary files
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove PID files
    rm -f .backend.pid .frontend.pid
    
    # Remove any temporary files created by the start script
    rm -f .temp_*
    
    print_success "Cleanup completed"
}

# Main script
main() {
    echo "=========================================="
    echo "  Progressive Difficulty System - Stop"
    echo "=========================================="
    
    # Check what services are running
    running_services=($(check_services))
    
    if [ ${#running_services[@]} -eq 0 ]; then
        print_warning "No services appear to be running"
        cleanup
        exit 0
    fi
    
    print_status "Found running services: ${running_services[*]}"
    
    # Stop Docker services if running
    if [[ " ${running_services[@]} " =~ " Docker " ]]; then
        if command -v docker-compose &> /dev/null; then
            stop_docker
        else
            print_error "Docker Compose not found but Docker services appear to be running"
        fi
    fi
    
    # Stop local services if running
    if [[ " ${running_services[@]} " =~ " Local " ]]; then
        stop_local
    fi
    
    # Final cleanup
    cleanup
    
    echo ""
    print_success "All services stopped successfully!"
    echo ""
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}[WARNING]${NC} Script interrupted. Cleaning up..."; cleanup; exit 1' INT TERM

# Run main function
main "$@" 