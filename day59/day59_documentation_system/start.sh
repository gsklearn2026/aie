#!/bin/bash

echo "======================================"
echo "Starting Documentation System"
echo "======================================"

# Parse command line arguments
USE_DOCKER=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --docker) USE_DOCKER=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Set backend port (use 8001 if 8000 is in use)
BACKEND_PORT=8001

if [ "$USE_DOCKER" = true ]; then
    echo "Starting with Docker..."
    docker-compose up -d
    echo ""
    echo "✓ Services started"
    BACKEND_PORT=8000  # Docker uses port 8000
else
    echo "Starting without Docker..."
    
    # Start backend
    cd backend
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
    uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend with API URL environment variable
    cd frontend
    REACT_APP_API_URL=http://localhost:$BACKEND_PORT PORT=3000 npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✓ Services started (PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID)"
    echo ""
    echo "To stop services, run './stop.sh'"
fi

echo ""
echo "======================================"
echo "Documentation System is running!"
echo "======================================"
echo ""
echo "Access points:"
echo "  Documentation Portal: http://localhost:3000"
echo "  API Swagger UI:       http://localhost:$BACKEND_PORT/api/docs"
echo "  API ReDoc:            http://localhost:$BACKEND_PORT/api/redoc"
echo "  Health Check:         http://localhost:$BACKEND_PORT/health"
echo "  System Metrics:       http://localhost:$BACKEND_PORT/metrics"
echo ""
