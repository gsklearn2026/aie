# Day 53: Connection Pooling and Resource Management

## Quick Start

### Option 1: With Docker (Recommended)
```bash
./build.sh
# Select option 1
```

### Option 2: Without Docker
```bash
./build.sh
# Select option 2
```

### Run Tests
```bash
./build.sh
# Select option 3
```

## Manual Steps

### With Docker:
```bash
# Start services
docker-compose up -d

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Start application
cd ..
./start.sh docker
```

### Without Docker:
```bash
# Ensure PostgreSQL and Redis are running locally

# Setup database
createdb quizdb
createuser quizuser -P  # password: quizpass

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Start application
cd ..
./start.sh local
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features

- Database connection pooling
- Gemini AI connection pooling with rate limiting
- Real-time pool metrics dashboard
- Quiz generation and storage
- Connection reuse monitoring

## Stop Services

```bash
./stop.sh
```
