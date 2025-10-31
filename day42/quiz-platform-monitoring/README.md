# Quiz Platform Monitoring System - Day 42

A comprehensive monitoring and alerting system for the AI-powered quiz platform.

## Features

- Real-time metrics collection and visualization
- System health monitoring (CPU, Memory, Active Users)
- Smart alerting with configurable thresholds
- Interactive dashboard with live charts
- Prometheus metrics integration
- Grafana dashboards (Docker setup)

## Quick Start

1. Run the build script:
   ```bash
   ./build.sh
   ```

2. Select option 1 for Docker setup (recommended)

3. Access the dashboard at http://localhost:3000

## Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for containerized setup)

### Build and Run
```bash
# Build everything
./build.sh

# Start services
./start.sh

# Stop services
./stop.sh
```

## Testing

Run comprehensive tests:
```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# Frontend tests  
cd frontend && npm test
```

## Architecture

- **Backend**: FastAPI with Prometheus metrics
- **Frontend**: React dashboard with real-time charts
- **Monitoring**: Prometheus + Grafana stack
- **Containerization**: Docker Compose setup

## Dashboard Features

- 📊 Real-time system metrics
- 👥 Active user tracking  
- ⚡ Response time monitoring
- 🚨 Smart alert system
- 📈 Historical data visualization

## API Endpoints

- `GET /health` - System health check
- `GET /metrics` - Prometheus metrics
- `GET /api/dashboard/stats` - Dashboard statistics
- `POST /api/simulate/load` - Load testing
- `POST /api/simulate/error` - Alert testing

Built for production-ready monitoring and alerting! 🚀
