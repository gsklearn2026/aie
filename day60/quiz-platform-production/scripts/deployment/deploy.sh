#!/bin/bash

echo "Starting Blue-Green Deployment..."

# Build new version (green)
echo "Building green environment..."
docker-compose build backend-green

# Start green environment
echo "Starting green environment..."
docker-compose up -d backend-green

# Wait for health check
echo "Waiting for green environment to be ready..."
for i in {1..30}; do
    if docker-compose exec -T backend-green curl -f http://localhost:8000/health/ready; then
        echo "Green environment is healthy!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Run smoke tests on green
echo "Running smoke tests on green..."
docker-compose exec -T backend-green pytest tests/ -v

# Switch traffic to green
echo "Switching traffic to green..."
sed -i 's/backend_blue/backend_green/g' nginx/nginx.conf
docker-compose restart nginx

echo "Deployment complete! Traffic now on green."
echo "Blue environment still running for rollback if needed."
