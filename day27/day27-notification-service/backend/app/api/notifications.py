from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ..models.notification import NotificationRequest
from ..services.notification_service import NotificationService
from ..services.websocket_manager import WebSocketManager
import redis
import json

router = APIRouter()

# Initialize services (in production, use dependency injection)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
websocket_manager = WebSocketManager()
notification_service = NotificationService(websocket_manager)

@router.post("/send")
async def send_notification(notification: NotificationRequest):
    """Send a notification"""
    try:
        # Convert to event format and add to queue
        event = {
            "event_type": notification.event_type,
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.message,
            "data": notification.data,
            "timestamp": "2025-05-15T10:30:00Z"
        }
        
        # Add to Redis queue for processing
        redis_client.rpush('notification_events', json.dumps(event))
        
        return {"message": "Notification queued successfully", "event_id": event.get("timestamp")}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_notifications(user_id: str, limit: int = 20):
    """Get notifications for a user"""
    try:
        notifications = notification_service.get_user_notifications(user_id, limit)
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-event")
async def create_test_event():
    """Create a test notification event"""
    test_event = {
        "event_type": "quiz_completed",
        "user_id": "user123",
        "quiz_id": "quiz456",
        "quiz_name": "Python Basics",
        "score": 85,
        "timestamp": "2025-05-15T10:30:00Z"
    }
    
    redis_client.rpush('notification_events', json.dumps(test_event))
    return {"message": "Test event created", "event": test_event}
