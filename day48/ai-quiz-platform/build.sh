#!/bin/bash

echo "🔧 Building AI Quiz Platform with Error Handling"
echo "==============================================="

# Check if Docker should be used
USE_DOCKER=${1:-"no"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "🐳 Building with Docker..."
    
    # Create Docker files
    cat > backend/Dockerfile << 'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app/main.py"]
DOCKERFILE

    cat > frontend/Dockerfile << 'DOCKERFILE'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
DOCKERFILE

    cat > frontend/nginx.conf << 'EOF'
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

    docker-compose build
else
    echo "📦 Building without Docker..."
    
    # Build backend
    echo "Building backend..."
    cd backend || exit 1
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || {
            echo "❌ Failed to install backend dependencies"
            exit 1
        }
    fi
    cd ..
    
    # Build frontend
    echo "Building frontend..."
    cd frontend || exit 1
    if [ -f "package.json" ]; then
        npm install || {
            echo "❌ Failed to install frontend dependencies"
            exit 1
        }
        npm run build || {
            echo "❌ Failed to build frontend"
            exit 1
        }
    fi
    cd ..
    
    echo "✅ Build completed successfully!"
fi
