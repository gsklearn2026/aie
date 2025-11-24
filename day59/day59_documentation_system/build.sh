#!/bin/bash

echo "======================================"
echo "Documentation System Build Script"
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

if [ "$USE_DOCKER" = true ]; then
    echo "Building with Docker..."
    docker-compose build
    echo "✓ Docker build complete"
else
    echo "Building without Docker..."
    
    # Backend setup
    cd backend
    python3 -m venv venv
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend setup
    cd frontend
    npm install
    cd ..
    
    echo "✓ Local build complete"
fi

echo ""
echo "Build completed successfully!"
echo "Run './start.sh' to start the application"
