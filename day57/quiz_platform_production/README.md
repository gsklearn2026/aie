# Quiz Platform - Production Environment

Production-ready Quiz Platform with auto-scaling, load balancing, and comprehensive monitoring.

## Architecture

- **Load Balancer**: Nginx (least connections algorithm)
- **Backend**: 3 FastAPI instances with auto-scaling
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis cluster
- **Monitoring**: Prometheus metrics collection
- **Container Orchestration**: Docker Compose

## Quick Start

### With Docker (Recommended)
```bash
./build.sh  # Choose option 1
./start.sh  # Choose option 1
```

### Without Docker
```bash
./build.sh  # Choose option 2
# Start PostgreSQL and Redis separately
./start.sh  # Choose option 2
```

## Access Points

- Frontend: http://localhost:80
- API: http://localhost:80/api/
- Health Check: http://localhost:80/health
- Metrics: http://localhost:9090

## Monitoring

View Prometheus metrics:
```bash
open http://localhost:9090
```

View container logs:
```bash
docker-compose logs -f
```

## Testing

Run tests:
```bash
cd backend
source venv/bin/activate
pytest -v
```

## Scaling

Manual scaling:
```bash
docker-compose up -d --scale backend=5
```

## Stopping Services

```bash
./stop.sh
```

## Production Deployment

1. Update environment configs in `configs/environments/`
2. Configure SSL certificates in `nginx/ssl/`
3. Set production database credentials
4. Deploy using container orchestration (Kubernetes, ECS, etc.)

## Health Checks

- **Liveness**: `/health/live` - Is service running?
- **Readiness**: `/health/ready` - Can service handle requests?
- **Deep Health**: `/health` - Check all dependencies

## Environment Variables

See `configs/environments/` for different environment configurations:
- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment
