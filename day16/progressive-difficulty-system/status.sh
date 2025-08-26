#!/bin/bash

# Progressive Difficulty System - Status Script
# This script checks the status of all services

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

# Function to check service status
check_service() {
    local service_name=$1
    local port=$2
    local url=$3
    
    echo -n "  $service_name: "
    
    if curl -f $url > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        return 1
    fi
}

# Function to check Docker services
check_docker_services() {
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose not found"
        return 1
    fi
    
    if [ ! -f "docker-compose.yml" ]; then
        print_warning "docker-compose.yml not found"
        return 1
    fi
    
    print_status "Checking Docker services..."
    
    # Get Docker service status
    local docker_status=$(docker-compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "")
    
    if [ -z "$docker_status" ]; then
        print_warning "No Docker services found"
        return 1
    fi
    
    echo "$docker_status"
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        return 0
    else
        return 1
    fi
}

# Function to check local services
check_local_services() {
    print_status "Checking local services..."
    
    local all_running=true
    
    # Check Redis
    echo -n "  Redis: "
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not running${NC}"
        all_running=false
    fi
    
    # Check Backend
    check_service "Backend" "8000" "http://localhost:8000/health" || all_running=false
    
    # Check Frontend
    check_service "Frontend" "3000" "http://localhost:3000" || all_running=false
    
    # Check PID files
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "  Backend PID: $BACKEND_PID (from PID file)"
        else
            echo -e "  ${YELLOW}Backend PID file exists but process not found${NC}"
        fi
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "  Frontend PID: $FRONTEND_PID (from PID file)"
        else
            echo -e "  ${YELLOW}Frontend PID file exists but process not found${NC}"
        fi
    fi
    
    if [ "$all_running" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to check port usage
check_ports() {
    print_status "Checking port usage..."
    
    local ports=("3000" "8000" "6379")
    
    for port in "${ports[@]}"; do
        echo -n "  Port $port: "
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            local process=$(lsof -Pi :$port -sTCP:LISTEN | tail -n +2 | awk '{print $1}' | head -1)
            echo -e "${GREEN}✓ In use by $process${NC}"
        else
            echo -e "${YELLOW}✗ Available${NC}"
        fi
    done
}

# Main script
main() {
    echo "=========================================="
    echo "  Progressive Difficulty System - Status"
    echo "=========================================="
    echo ""
    
    # Check Docker services
    if check_docker_services; then
        echo ""
        print_success "Docker services are running"
    else
        echo ""
        print_warning "Docker services are not running"
    fi
    
    echo ""
    
    # Check local services
    if check_local_services; then
        echo ""
        print_success "Local services are running"
    else
        echo ""
        print_warning "Local services are not running"
    fi
    
    echo ""
    
    # Check port usage
    check_ports
    
    echo ""
    echo "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8000"
    echo "  Redis:    localhost:6379"
    echo ""
}

# Run main function
main "$@" 