#!/bin/bash

# Progressive Difficulty System - Start Script
# This script starts the entire system including backend, frontend, and Redis

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        print_warning "On macOS, you can start Docker by running: open -a Docker"
        print_warning "On Linux, you can start Docker by running: sudo systemctl start docker"
        exit 1
    fi
}

# Function to check and fix common Docker issues
check_docker_issues() {
    print_status "Checking for common Docker issues..."
    
    # Check if containers are already running
    if docker-compose ps | grep -q "Up"; then
        print_warning "Some containers are already running."
        read -p "Do you want to stop existing containers and restart? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Stopping existing containers..."
            docker-compose down
        fi
    fi
    
    # Check for stale containers
    if docker ps -a | grep -q "progressive-difficulty-system"; then
        print_status "Found existing containers. Cleaning up..."
        docker-compose down --remove-orphans
    fi
}

# Function to check if ports are available
check_ports() {
    local ports=("3000" "8000" "6379")
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=($port)
        fi
    done
    
    if [ ${#occupied_ports[@]} -ne 0 ]; then
        print_warning "The following ports are already in use: ${occupied_ports[*]}"
        print_warning "This might cause conflicts. Please stop any services using these ports."
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to start with Docker (Production)
start_docker() {
    print_status "Starting services with Docker Compose (Production)..."
    
    # Check for common issues before starting
    check_docker_issues
    
    docker-compose up --build -d
    
    # Wait for services to be ready
    wait_for_docker_services
}

# Function to start with Docker (Development)
start_docker_dev() {
    print_status "Starting services with Docker Compose (Development)..."
    
    # Check for common issues before starting
    check_docker_issues
    
    docker-compose -f docker-compose.dev.yml up --build -d
    
    # Wait for services to be ready
    wait_for_docker_services
}

# Function to wait for Docker services
wait_for_docker_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis is ready"
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        print_error "Redis failed to start within 60 seconds"
        print_troubleshooting_tips "redis"
        exit 1
    fi
    
    # Wait for Backend
    print_status "Waiting for Backend..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -eq 0 ]; then
        print_error "Backend failed to start within 60 seconds"
        print_troubleshooting_tips "backend"
        exit 1
    fi
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    timeout=90
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        sleep 3
        timeout=$((timeout - 3))
    done
    
    if [ $timeout -eq 0 ]; then
        print_error "Frontend failed to start within 90 seconds"
        print_troubleshooting_tips "frontend"
        exit 1
    fi
}

# Function to start locally
start_local() {
    print_status "Starting services locally..."
    
    # Check prerequisites
    check_prerequisites
    
    # Setup and start Redis
    setup_redis
    
    # Setup and start Backend
    setup_backend
    
    # Setup and start Frontend
    setup_frontend
    
    # Wait for all services to be ready
    wait_for_services
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+"
        print_warning "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 16+"
        print_warning "Visit: https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm"
        exit 1
    fi
    
    # Check curl for health checks
    if ! command -v curl &> /dev/null; then
        print_warning "curl is not installed. Health checks may fail."
    fi
    
    print_success "All prerequisites are satisfied"
}

# Function to setup Redis
setup_redis() {
    print_status "Setting up Redis..."
    
    # Check if Redis is already running
    if redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is already running"
        return 0
    fi
    
    # Try to start Redis based on the system
    if command -v brew &> /dev/null; then
        print_status "Starting Redis with Homebrew..."
        if brew services start redis 2>/dev/null; then
            sleep 2
        else
            print_warning "Redis is not installed via Homebrew"
            print_status "Installing Redis..."
            if brew install redis; then
                print_success "Redis installed successfully"
                brew services start redis
                sleep 2
            else
                print_error "Failed to install Redis via Homebrew"
                print_warning "Please install Redis manually: brew install redis"
                exit 1
            fi
        fi
    elif command -v systemctl &> /dev/null; then
        print_status "Starting Redis with systemctl..."
        if sudo systemctl start redis 2>/dev/null; then
            sleep 2
        else
            print_warning "Redis is not installed or not running"
            print_warning "Please install Redis: sudo apt-get install redis-server"
            exit 1
        fi
    elif command -v service &> /dev/null; then
        print_status "Starting Redis with service..."
        if sudo service redis start 2>/dev/null; then
            sleep 2
        else
            print_warning "Redis is not installed or not running"
            print_warning "Please install Redis: sudo yum install redis"
            exit 1
        fi
    else
        print_warning "Could not automatically start Redis"
        print_warning "Please start Redis manually and run this script again"
        print_warning "Installation guides:"
        print_warning "  macOS: brew install redis"
        print_warning "  Ubuntu: sudo apt-get install redis-server"
        print_warning "  CentOS: sudo yum install redis"
        exit 1
    fi
    
    # Verify Redis is running
    if redis-cli ping > /dev/null 2>&1; then
        print_success "Redis started successfully"
    else
        print_error "Failed to start Redis"
        exit 1
    fi
}

# Function to setup Backend
setup_backend() {
    print_status "Setting up Backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    if pip install -r requirements.txt; then
        print_success "Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        cd ..
        exit 1
    fi
    
    # Start backend in background
    print_status "Starting Backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    # Save PID for stop script
    echo $BACKEND_PID > ../.backend.pid
    
    cd ..
    
    print_success "Backend started (PID: $BACKEND_PID)"
}

# Function to setup Frontend
setup_frontend() {
    print_status "Setting up Frontend..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        if npm install; then
            print_success "Node.js dependencies installed"
        else
            print_error "Failed to install Node.js dependencies"
            cd ..
            exit 1
        fi
    else
        print_status "Node.js dependencies already installed"
    fi
    
    # Start frontend in background
    print_status "Starting Frontend development server..."
    npm start &
    FRONTEND_PID=$!
    
    # Save PID for stop script
    echo $FRONTEND_PID > ../.frontend.pid
    
    cd ..
    
    print_success "Frontend started (PID: $FRONTEND_PID)"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for Backend
    print_status "Waiting for Backend..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -eq 0 ]; then
        print_error "Backend failed to start within 60 seconds"
        print_warning "Check backend logs for errors"
        cleanup_on_failure
        exit 1
    fi
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    timeout=90
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        sleep 3
        timeout=$((timeout - 3))
    done
    
    if [ $timeout -eq 0 ]; then
        print_error "Frontend failed to start within 90 seconds"
        print_warning "Check frontend logs for errors"
        cleanup_on_failure
        exit 1
    fi
}

# Function to cleanup on failure
cleanup_on_failure() {
    print_status "Cleaning up on failure..."
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm -f .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f .frontend.pid
    fi
}

# Function to show troubleshooting tips
print_troubleshooting_tips() {
    local service=$1
    echo ""
    print_warning "Troubleshooting tips for $service:"
    echo ""
    
    case $service in
        "frontend")
            echo "  • Check frontend logs: docker-compose logs frontend"
            echo "  • Common issues:"
            echo "    - Nginx configuration errors in docker/nginx.conf"
            echo "    - Permission issues with nginx pid file"
            echo "    - Port 3000 already in use"
            echo "  • Try rebuilding: docker-compose down && docker-compose up --build -d"
            ;;
        "backend")
            echo "  • Check backend logs: docker-compose logs backend"
            echo "  • Common issues:"
            echo "    - Python dependencies not installed"
            echo "    - Port 8000 already in use"
            echo "    - Database connection issues"
            echo "  • Try rebuilding: docker-compose down && docker-compose up --build -d"
            ;;
        "redis")
            echo "  • Check Redis logs: docker-compose logs redis"
            echo "  • Common issues:"
            echo "    - Port 6379 already in use"
            echo "    - Memory issues"
            echo "  • Try rebuilding: docker-compose down && docker-compose up --build -d"
            ;;
    esac
    echo ""
}

# Function to show development tips
show_dev_tips() {
    echo ""
    echo "Development Tips:"
    echo "  • Backend logs: Check the terminal for uvicorn output"
    echo "  • Frontend logs: Check the terminal for npm start output"
    echo "  • Redis logs: brew services list | grep redis"
    echo "  • API docs: http://localhost:8000/docs"
    echo "  • Health check: http://localhost:8000/health"
    echo ""
    echo "Useful commands:"
    echo "  • Stop services: ./stop.sh"
    echo "  • Check status: ./status.sh"
    echo "  • View logs: tail -f backend/logs/*.log (if logging is configured)"
    echo ""
}

# Main script
main() {
    echo "=========================================="
    echo "  Progressive Difficulty System - Start"
    echo "=========================================="
    
    # Check if Docker is available
    if command -v docker-compose &> /dev/null; then
        check_docker
        check_ports
        
        echo ""
        echo "Choose your startup method:"
        echo "  1) Docker (Production) - Optimized containers"
        echo "  2) Docker (Development) - With hot reloading"
        echo "  3) Local - Direct installation"
        echo ""
        read -p "Enter your choice (1-3): " -n 1 -r
        echo
        
        case $REPLY in
            1)
                start_docker
                ;;
            2)
                start_docker_dev
                ;;
            3)
                start_local
                ;;
            *)
                print_error "Invalid choice. Please run the script again."
                exit 1
                ;;
        esac
    else
        print_warning "Docker Compose not found, starting locally..."
        DOCKER_NOT_FOUND=true
        check_ports
        start_local
    fi
    
    echo ""
    print_success "All services are running!"
    echo ""
    echo "Services:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8000"
    echo "  Redis:    localhost:6379"
    echo ""
    echo "Useful URLs:"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • Health Check: http://localhost:8000/health"
    echo "  • Frontend Dashboard: http://localhost:3000"
    echo ""
    echo "To stop the services, run: ./stop.sh"
    echo "To check status, run: ./status.sh"
    echo ""
    
    # Show development tips for local mode
    if [[ $REPLY == "3" ]] || [[ ! -z "$DOCKER_NOT_FOUND" ]]; then
        show_dev_tips
    fi
}

# Run main function
main "$@" 