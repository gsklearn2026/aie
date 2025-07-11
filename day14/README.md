# AI Testing Framework

A comprehensive testing framework for AI services with backend API and frontend dashboard.

## 🚀 Quick Start

### Setup (One-time)
```bash
# Install dependencies, build, and verify the framework
./setup.sh
./start.sh
```

### Daily Usage
```bash
# Start all services (backend + frontend)
./demo.sh

# Stop all services
./stop.sh
```

## 📊 Services Overview

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Features**: AI providers, test runners, validators

### Frontend (React Dashboard)
- **URL**: http://localhost:3000
- **Features**: Test dashboard, provider monitoring, real-time results

## 🛠️ Scripts

| Script | Purpose | Usage |
|--------|---------|--------|
| `setup.sh` | Initial setup, install dependencies, build | `./setup.sh` |
| `start.sh` | Complete setup + build + test + verify | `./start.sh` |
| `demo.sh` | Start all services for demo/development | `./demo.sh` |
| `stop.sh` | Stop all running services | `./stop.sh` |

## 📁 Project Structure

```
ai-testing-framework/
├── backend/                 # FastAPI application
│   ├── app/                # Main application code
│   │   ├── testing/        # AI test framework
│   │   ├── validators/     # Content/performance validators
│   │   ├── services/       # AI service management
│   │   └── providers/      # AI provider implementations
│   ├── tests/              # Unit tests
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment configuration
├── frontend/               # React dashboard
│   ├── src/               # React components
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
└── logs/                  # Service logs (created when running)
```

## 🔧 Development

### Manual Service Control

**Backend only:**
```bash
cd ai-testing-framework/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

**Frontend only:**
```bash
cd ai-testing-framework/frontend
npm start
```

### Logs
Service logs are available in the `logs/` directory:
- `backend.log` - FastAPI server logs
- `frontend.log` - React development server logs  
- `demo.log` - Start/stop events

### Testing
```bash
# Backend tests
cd ai-testing-framework/backend
source venv/bin/activate
pytest

# Frontend tests
cd ai-testing-framework/frontend
npm test
```

## 🎯 Features

- **AI Provider Management**: Support for multiple AI providers with failover
- **Test Framework**: Comprehensive testing for AI responses
- **Content Validation**: Quality, semantic, and performance validation
- **Real-time Dashboard**: Monitor tests and provider health
- **Mock Providers**: Test without external API dependencies
- **Logging**: Comprehensive logging and monitoring

## 🔗 API Endpoints

- `GET /health` - System health check
- `GET /api/providers` - List available providers
- `POST /api/generate` - Generate AI text
- `POST /api/test/run-suite` - Run test suite
- `POST /api/validate/content` - Validate content quality
- `GET /docs` - Interactive API documentation

## 💡 Tips

- Use `./demo.sh` for daily development and testing
- Check `logs/` directory if services fail to start
- Add your actual API keys to `backend/.env` for full functionality
- The framework works with mock providers even without API keys 