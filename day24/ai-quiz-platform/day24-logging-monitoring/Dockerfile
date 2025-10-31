FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend package.json and install dependencies
COPY frontend/package.json ./frontend/
WORKDIR /app/frontend
RUN npm install

# Copy application code
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm run build

# Expose ports
EXPOSE 8080 3000

# Start script
WORKDIR /app
CMD ["./start.sh"]
