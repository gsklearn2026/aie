# Quiz Platform - Day 52: Memory Management Optimization

## Quick Start

### Build
```bash
cd quiz_platform_day52
./scripts/build.sh
# Choose option 1 (Docker) or 2 (Local)
```

### Start
```bash
./scripts/start.sh
```

### Test
```bash
./scripts/test.sh
```

### Stop
```bash
./scripts/stop.sh
```

## Access Points
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Features
- Real-time memory monitoring
- Memory profiling per endpoint
- AI-powered quiz generation with caching
- Automatic garbage collection
- Leak detection
- Cache management

## Architecture
The system implements memory optimization through:
1. Request-level memory profiling
2. Smart caching with TTL
3. Automatic cleanup scheduling
4. Real-time monitoring dashboard
5. Weak references for cache entries
