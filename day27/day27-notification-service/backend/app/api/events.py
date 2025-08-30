from fastapi import APIRouter, HTTPException
import redis
import json
from typing import Dict, Any

router = APIRouter()
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@router.post("/publish")
async def publish_event(event_data: Dict[str, Any]):
    """Publish an event to the notification system"""
    try:
        # Add timestamp if not present
        if 'timestamp' not in event_data:
            from datetime import datetime
            event_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Add to Redis queue
        redis_client.rpush('notification_events', json.dumps(event_data))
        
        return {"message": "Event published successfully", "event": event_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/status")
async def get_queue_status():
    """Get status of the event queue"""
    try:
        queue_length = redis_client.llen('notification_events')
        return {"queue_length": queue_length}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
