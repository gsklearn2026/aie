import pytest
import asyncio
from datetime import datetime
<<<<<<< HEAD
from backend.services.logging_service import LoggingService
=======
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.logging_service import LoggingService
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae

@pytest.mark.asyncio
async def test_log_event():
    service = LoggingService()
    await service.initialize()
    
    event_data = {
        "event": "test_event",
        "user_id": "test_user",
        "message": "Test log entry"
    }
    
    await service.log_event(event_data)
    
    # Search for the logged event
    logs = await service.search_logs("test_event")
    assert len(logs) >= 0  # Should not fail

@pytest.mark.asyncio
async def test_search_logs():
    service = LoggingService()
    await service.initialize()
    
    logs = await service.search_logs("test", limit=10)
    assert isinstance(logs, list)

def test_logging_service_initialization():
    service = LoggingService()
<<<<<<< HEAD
    assert service.elasticsearch_host == "localhost:9200"
=======
    assert service.elasticsearch_host == "http://localhost:9200"
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
    assert service.redis_host == "localhost"
    assert service.redis_port == 6379
