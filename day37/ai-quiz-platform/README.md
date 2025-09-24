# AI Quiz Platform - Day 37: Docker Containerization

A fully containerized AI-powered quiz platform built with React, FastAPI, PostgreSQL, and Redis.

## 🏗️ Architecture

- **Frontend**: React app with Material-UI, served by Nginx
- **Backend**: Python FastAPI with Gemini AI integration
- **Database**: PostgreSQL with health checks
- **Cache**: Redis for session management
- **Orchestration**: Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Gemini AI API key

### Setup
```bash
# Clone and setup
git clone <repo-url>
cd ai-quiz-platform

# Build and start
./build.sh

# Choose option 1 (Docker) for easiest setup
```

### Configuration
Update `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🧪 Testing

```bash
# Run all tests
./test.sh

# Test specific deployment
./test.sh  # Choose option 1 for Docker
```

## 🛠️ Development

### Docker Commands
```bash
# View logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Enter container
docker-compose exec [service_name] bash

# Stop all
docker-compose down
```

### Local Development
```bash
# Build local environment
./build.sh  # Choose option 2

# Start locally
./start.sh  # Choose option 2
```

## 📁 Project Structure

```
ai-quiz-platform/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   ├── tests/              # Test files
│   └── requirements/       # Dependencies
├── frontend/               # React frontend
│   ├── src/               # Source code
│   └── public/            # Static files
├── database/              # PostgreSQL setup
│   └── init/              # Init scripts
├── docker-compose.yml     # Orchestration
├── build.sh              # Build script
├── start.sh              # Start script
├── stop.sh               # Stop script
└── test.sh               # Test script
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for AI quiz generation
- `POSTGRES_*`: Database configuration
- `REDIS_*`: Cache configuration

### Container Resources
- Backend: 512MB RAM, 0.5 CPU
- Frontend: 256MB RAM, 0.25 CPU
- Database: 1GB RAM, 1 CPU
- Redis: 256MB RAM, 0.25 CPU

## 🚨 Troubleshooting

### Common Issues
1. **Services won't start**: Check Docker daemon is running
2. **API errors**: Verify Gemini API key is set
3. **Database connection**: Ensure PostgreSQL container is healthy
4. **Port conflicts**: Check ports 3000, 8000, 5432, 6379 are free

### Debug Commands
```bash
# Check service health
docker-compose ps

# View specific logs
docker-compose logs -f backend

# Check container resources
docker stats

# Restart unhealthy service
docker-compose restart [service_name]
```

## 📈 Monitoring

Health check endpoints:
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000/health
- Database: Built-in PostgreSQL health checks
- Redis: Built-in Redis health checks

## 🔒 Security

- Non-root container users
- Read-only filesystems where possible
- Environment-based secret management
- Internal Docker network isolation
- Resource limits to prevent DoS

## 📚 Learning Outcomes

After completing this lesson, you'll understand:
- Container fundamentals and Docker best practices
- Multi-stage builds for optimized images
- Service orchestration with Docker Compose
- Health checks and dependency management
- Production-ready containerization patterns

## 🎯 Next Steps

Tomorrow (Day 38): Docker Compose advanced features including:
- Service scaling
- Load balancing
- Production deployment patterns
- Monitoring and logging integration
