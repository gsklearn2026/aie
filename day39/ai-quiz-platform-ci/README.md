# AI Quiz Platform - Day 39: CI Pipeline with GitHub Actions

This project demonstrates implementing a robust CI pipeline using GitHub Actions for an AI-powered quiz platform.

## Features

- ✅ Automated testing on every commit
- 🐳 Docker containerization with health checks
- 🧪 Multi-stage testing (unit, integration, e2e)
- 🔒 Security scanning with Trivy
- 📊 Code coverage reporting
- 🚀 Parallel test execution
- 🔄 Integration with external AI services

## Quick Start

### Option 1: Local Development
```bash
./build.sh local
./start.sh local
```

### Option 2: Docker Development
```bash
./build.sh docker
./start.sh docker
```

## CI Pipeline Overview

The GitHub Actions workflow includes:
1. **Backend Tests** - Python/FastAPI testing with pytest
2. **Frontend Tests** - React testing with Jest
3. **Docker Build** - Multi-stage container builds
4. **Security Scan** - Vulnerability scanning
5. **Integration Tests** - Full stack validation

## Environment Setup

### Required Environment Variables
```bash
# GitHub Secrets
GEMINI_API_KEY=your_gemini_api_key_here
```

### Database Setup
```bash
# For local development
DATABASE_URL=postgresql://user:pass@localhost/quiz_dev
```

## Testing

### Run All Tests
```bash
./build.sh test
```

### Backend Tests Only
```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app
```

### Frontend Tests Only
```bash
cd frontend
npm run test:ci
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up -d
python -m pytest tests/integration/ -v
docker-compose -f docker-compose.test.yml down
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /quiz/generate` - Generate AI quiz
- `GET /quiz/list` - List quizzes

## Frontend Features

- Real-time API status monitoring
- Quiz generation interface
- Responsive design
- Error handling

## CI/CD Best Practices Implemented

1. **Fast Feedback** - Parallel test execution
2. **Quality Gates** - Tests must pass to proceed
3. **Security First** - Automated vulnerability scanning
4. **Reproducible Builds** - Docker containerization
5. **Comprehensive Testing** - Unit, integration, and E2E tests

## Stopping the Application

```bash
./stop.sh
```

## Troubleshooting

### Common Issues

1. **Port conflicts** - Change ports in docker-compose.yml
2. **Database connection** - Ensure PostgreSQL is running
3. **API key missing** - Set GEMINI_API_KEY environment variable
4. **Build failures** - Check Docker daemon is running

### CI Debugging

1. Check GitHub Actions logs
2. Run tests locally: `./build.sh test`
3. Validate Docker builds: `./build.sh docker`
4. Test integration: `docker-compose -f docker-compose.test.yml up`

---

**Next Steps:** Implement CD pipeline (Day 40) for automated deployments.
