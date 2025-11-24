# Performance Benchmarks

## API Response Times

### Quiz Generation Endpoint
```
Method: POST /api/v1/quiz/generate

Load: 100 concurrent users
Duration: 5 minutes

Results:
- p50: 120ms
- p75: 180ms
- p90: 250ms
- p95: 280ms
- p99: 450ms
- Max: 850ms
```

### Health Check Endpoint
```
Method: GET /health

Results:
- p50: 5ms
- p95: 15ms
- p99: 25ms
```

## Database Query Performance

### Quiz Retrieval
- With index: 15ms (p50)
- Without index: 340ms (p50)
- Improvement: 95.6%

### Caching Impact
- Cache hit: <10ms
- Cache miss: ~120ms
- Hit rate: 94.2%

## Load Testing Results

### Sustained Load
- 2,400 req/sec sustained for 1 hour
- 0.02% error rate
- Average response time: 125ms

### Spike Testing
- Peak: 5,000 req/sec for 2 minutes
- System remained stable
- Auto-scaling triggered at 3,000 req/sec

## Resource Utilization

### Single Instance
- CPU: 30-40% average
- Memory: 512MB average
- Network: 50Mbps average

### Scaling Characteristics
- Linear scaling up to 10 instances
- Optimal: 4 instances for typical load
- Cost-effective: 2 instances + auto-scaling
