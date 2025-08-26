#!/bin/bash

# AI Testing Framework - Stop Script
# Stops both backend and frontend services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

echo "🛑 AI Testing Framework - Stopping All Services..."
echo "================================================="

# Function to kill process by PID
kill_process() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        log_info "Stopping $name (PID: $pid)..."
        kill -TERM "$pid" 2>/dev/null
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 "$pid" 2>/dev/null; then
                log_success "$name stopped gracefully"
                return 0
            fi
            sleep 1
        done
        
        # Force kill if still running
        log_warning "$name didn't stop gracefully, force killing..."
        kill -KILL "$pid" 2>/dev/null
        sleep 1
        
        if ! kill -0 "$pid" 2>/dev/null; then
            log_success "$name force stopped"
        else
            log_error "Failed to stop $name"
            return 1
        fi
    else
        log_warning "$name is not running or PID is invalid"
    fi
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

STOPPED_SERVICES=0

# Stop services using PID files
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid 2>/dev/null)
    if kill_process "$BACKEND_PID" "Backend server"; then
        STOPPED_SERVICES=$((STOPPED_SERVICES + 1))
    fi
    rm -f logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid 2>/dev/null)
    if kill_process "$FRONTEND_PID" "Frontend server"; then
        STOPPED_SERVICES=$((STOPPED_SERVICES + 1))
    fi
    rm -f logs/frontend.pid
fi

# Additional cleanup - find and kill any remaining processes
log_info "Checking for any remaining processes..."

# Kill any uvicorn processes (backend)
UVICORN_PIDS=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || true)
if [ -n "$UVICORN_PIDS" ]; then
    log_info "Found additional uvicorn processes, stopping them..."
    echo "$UVICORN_PIDS" | while read -r pid; do
        if kill_process "$pid" "Uvicorn process"; then
            STOPPED_SERVICES=$((STOPPED_SERVICES + 1))
        fi
    done
fi

# Kill any React development server processes (frontend)
REACT_PIDS=$(pgrep -f "react-scripts.*start" 2>/dev/null || true)
if [ -n "$REACT_PIDS" ]; then
    log_info "Found additional React development server processes, stopping them..."
    echo "$REACT_PIDS" | while read -r pid; do
        if kill_process "$pid" "React dev server"; then
            STOPPED_SERVICES=$((STOPPED_SERVICES + 1))
        fi
    done
fi

# Kill any Node.js processes that might be serving the frontend
NODE_PIDS=$(pgrep -f "node.*ai-testing-dashboard" 2>/dev/null || true)
if [ -n "$NODE_PIDS" ]; then
    log_info "Found additional Node.js processes, stopping them..."
    echo "$NODE_PIDS" | while read -r pid; do
        if kill_process "$pid" "Node.js process"; then
            STOPPED_SERVICES=$((STOPPED_SERVICES + 1))
        fi
    done
fi

# Wait a moment for ports to be released
sleep 2

# Verify ports are free
echo ""
log_info "Verifying services are stopped..."

if check_port 8000; then
    log_warning "Port 8000 is still in use - there may be other services running"
    lsof -Pi :8000 -sTCP:LISTEN
else
    log_success "Port 8000 is now free"
fi

if check_port 3000; then
    log_warning "Port 3000 is still in use - there may be other services running"
    lsof -Pi :3000 -sTCP:LISTEN
else
    log_success "Port 3000 is now free"
fi

# Clean up log files (optional)
log_info "Cleaning up temporary files..."
rm -f logs/backend.pid logs/frontend.pid

# Log the stop event
echo "Demo stopped at $(date)" >> logs/demo.log

echo ""
echo "🏁 Stop Operation Complete!"
echo "=========================="

if [ $STOPPED_SERVICES -gt 0 ]; then
    log_success "Successfully stopped $STOPPED_SERVICES service(s)"
else
    log_info "No running services found to stop"
fi

echo ""
log_info "📁 Service logs are preserved in the logs/ directory"
log_info "🚀 To start services again, run: ./demo.sh"
echo ""

# Check if any AI Testing Framework processes are still running
REMAINING=$(pgrep -f "(uvicorn.*app.main|react-scripts.*start|node.*ai-testing)" 2>/dev/null | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    log_warning "$REMAINING AI Testing Framework process(es) may still be running"
    echo "   Run 'ps aux | grep -E \"(uvicorn|react-scripts|node)\"' to check"
else
    log_success "All AI Testing Framework services have been stopped"
fi 