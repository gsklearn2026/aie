# Day 36: Environment Configuration - Quiz Platform

## Overview
Environment-aware configuration management system supporting development, testing, and production environments.

## Quick Start

### Without Docker
```bash
./build.sh --env development
./start.sh --env development
```

### With Docker
```bash
./build.sh --docker --env production
./start.sh --docker
```

## Environment Files
- `.env.development` - Development settings
- `.env.testing` - Testing configuration  
- `.env.production` - Production settings

## Endpoints
- `GET /` - Application info
- `GET /health` - Health check
- `GET /config` - Configuration (dev only)
- `POST /quiz/generate` - Generate quiz question

## Configuration Features
- Hierarchical config loading (base → env → env vars)
- Secure credential management
- Environment-specific database connections
- Rate limiting per environment
- Feature flags support

## Testing
```bash
cd backend
python -m pytest src/tests/ -v
```

## Stop Services
```bash
./stop.sh
```
