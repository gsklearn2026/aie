from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
import psutil
import logging

logger = logging.getLogger(__name__)

# Metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

memory_usage = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage'
)

db_connections = Gauge(
    'database_connections_active',
    'Active database connections'
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits'
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses'
)

ai_requests = Counter(
    'ai_requests_total',
    'Total AI generation requests',
    ['status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request latency'
)

class MetricsMiddleware:
    """Middleware to track request metrics"""
    
    async def __call__(self, request, call_next):
        active_requests.inc()
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        active_requests.dec()
        
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

def update_system_metrics():
    """Update system resource metrics"""
    try:
        cpu_usage.set(psutil.cpu_percent())
        memory_usage.set(psutil.virtual_memory().percent)
    except Exception as e:
        logger.error(f"Failed to update system metrics: {e}")

async def get_metrics():
    """Generate Prometheus metrics"""
    update_system_metrics()
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
