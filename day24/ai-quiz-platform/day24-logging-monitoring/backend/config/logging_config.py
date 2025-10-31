import os
import structlog
from datetime import datetime
from typing import Any, Dict

<<<<<<< HEAD
# Configure structured logging with basic setup
=======
# Configure structured logging
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
<<<<<<< HEAD
        structlog.processors.TimeStamper(fmt="iso"),
=======
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

class LoggingConfig:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
<<<<<<< HEAD
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
=======
    LOG_FILE = os.getenv("LOG_FILE", "../logs/app.log")
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
    ENABLE_CONSOLE = os.getenv("ENABLE_CONSOLE", "true").lower() == "true"
    ENABLE_FILE = os.getenv("ENABLE_FILE", "true").lower() == "true"
    
    # Elasticsearch configuration
<<<<<<< HEAD
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
=======
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
    ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "quiz-platform-logs")
    
    # Redis configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    
    # Metrics configuration
    METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))
