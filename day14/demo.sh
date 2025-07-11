#!/bin/bash

# AI Testing Framework - Demo Script
# Starts both backend and frontend services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_demo() {
    echo -e "${PURPLE}🚀 $1${NC}"
}

echo "🚀 AI Testing Framework - Starting Demo Environment..."
echo "======================================================"

# Check if project exists
if [ ! -d "ai-testing-framework" ]; then
    log_error "ai-testing-framework directory not found. Please run setup.sh first."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if services are already running
if check_port 8000; then
    log_warning "Backend already running on port 8000"
    BACKEND_RUNNING=true
else
    BACKEND_RUNNING=false
fi

if check_port 3000; then
    log_warning "Frontend already running on port 3000"
    FRONTEND_RUNNING=true
else
    FRONTEND_RUNNING=false
fi

# Start Backend
if [ "$BACKEND_RUNNING" = false ]; then
    log_info "Starting FastAPI backend server..."
    cd ai-testing-framework/backend
    
    # Activate virtual environment and start server in background
    (
        source venv/bin/activate
        log_demo "Backend starting on http://localhost:8000"
        python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../../logs/backend.log 2>&1 &
        echo $! > ../../logs/backend.pid
    )
    
    cd ../..
    
    # Wait for backend to start
    log_info "Waiting for backend to initialize..."
    for i in {1..30}; do
        if check_port 8000; then
            log_success "Backend server started successfully!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            log_error "Backend failed to start within 30 seconds"
            exit 1
        fi
    done
else
    log_info "Backend already running, skipping startup"
fi

# Start Frontend
if [ "$FRONTEND_RUNNING" = false ]; then
    log_info "Starting React frontend development server..."
    cd ai-testing-framework/frontend
    
    # Start React dev server in background
    (
        log_demo "Frontend starting on http://localhost:3000"
        BROWSER=none npm start > ../../logs/frontend.log 2>&1 &
        echo $! > ../../logs/frontend.pid
    )
    
    cd ../..
    
    # Wait for frontend to start
    log_info "Waiting for frontend to initialize..."
    for i in {1..60}; do
        if check_port 3000; then
            log_success "Frontend server started successfully!"
            break
        fi
        sleep 2
        if [ $i -eq 60 ]; then
            log_error "Frontend failed to start within 120 seconds"
            exit 1
        fi
    done
else
    log_info "Frontend already running, skipping startup"
fi

# Health check
log_info "Performing health checks..."

# Check backend health
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    log_success "Backend health check passed"
else
    log_warning "Backend health check failed"
fi

# Check frontend accessibility
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    log_success "Frontend accessibility check passed"
else
    log_warning "Frontend accessibility check failed"
fi

echo ""
echo "🎉 AI Testing Framework Demo Environment Ready!"
echo "=============================================="
echo ""
log_demo "🎯 Dashboard:        http://localhost:3000"
log_demo "📚 API Documentation: http://localhost:8000/docs"
log_demo "🔍 Health Check:     http://localhost:8000/health"
log_demo "⚡ API Endpoints:     http://localhost:8000/api/*"
echo ""
log_info "📁 Logs are available in the logs/ directory:"
echo "   - Backend:  logs/backend.log"
echo "   - Frontend: logs/frontend.log"
echo ""
log_info "🛑 To stop all services, run: ./stop.sh"
echo ""
log_success "Demo environment is now running!"

# Store PIDs for easy cleanup
echo "Demo started at $(date)" >> logs/demo.log
echo "Backend PID: $(cat logs/backend.pid 2>/dev/null || echo 'N/A')" >> logs/demo.log
echo "Frontend PID: $(cat logs/frontend.pid 2>/dev/null || echo 'N/A')" >> logs/demo.log 