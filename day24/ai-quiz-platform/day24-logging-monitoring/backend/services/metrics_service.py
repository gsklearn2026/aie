from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil
import structlog
from typing import Dict, Any
import time

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'System memory usage')
QUIZ_SUBMISSIONS = Counter('quiz_submissions_total', 'Total quiz submissions', ['quiz_type'])
AI_INFERENCE_TIME = Histogram('ai_inference_duration_seconds', 'AI model inference time')

class MetricsService:
    def __init__(self):
        self.start_time = time.time()
        
    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics server"""
        start_http_server(port)
        logger.info("Metrics server started", port=port)
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.observe(duration)
        
        logger.info(
            "Request metrics recorded",
            method=method,
            endpoint=endpoint,
            status=status,
            duration_ms=round(duration * 1000, 2)
        )
    
    def record_quiz_submission(self, quiz_type: str):
        """Record quiz submission"""
        QUIZ_SUBMISSIONS.labels(quiz_type=quiz_type).inc()
        
        logger.info(
            "Quiz submission recorded",
            quiz_type=quiz_type
        )
    
    def record_ai_inference(self, duration: float):
        """Record AI inference time"""
        AI_INFERENCE_TIME.observe(duration)
        
        logger.info(
            "AI inference metrics recorded",
            duration_ms=round(duration * 1000, 2)
        )
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        SYSTEM_CPU.set(cpu_percent)
        SYSTEM_MEMORY.set(memory_percent)
        
        logger.debug(
            "System metrics updated",
            cpu_percent=cpu_percent,
            memory_percent=memory_percent
        )
    
    def set_active_users(self, count: int):
        """Set active user count"""
        ACTIVE_USERS.set(count)
        
        logger.info(
            "Active users updated",
            count=count
        )

# Global metrics instance
metrics_service = MetricsService()
