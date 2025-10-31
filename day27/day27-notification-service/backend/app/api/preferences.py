from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.notification import NotificationPreference

router = APIRouter()

# In-memory storage for demo (use database in production)
user_preferences: Dict[str, Dict[str, Any]] = {}

@router.get("/user/{user_id}")
async def get_user_preferences(user_id: str):
    """Get notification preferences for a user"""
    preferences = user_preferences.get(user_id, {})
    return {"user_id": user_id, "preferences": preferences}

@router.post("/user/{user_id}")
async def update_user_preferences(user_id: str, preferences: Dict[str, Any]):
    """Update notification preferences for a user"""
    try:
        user_preferences[user_id] = preferences
        return {"message": "Preferences updated successfully", "preferences": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user/{user_id}/toggle/{event_type}")
async def toggle_notification_type(user_id: str, event_type: str, enabled: bool = True):
    """Toggle a specific notification type for a user"""
    try:
        if user_id not in user_preferences:
            user_preferences[user_id] = {}
        
        if event_type not in user_preferences[user_id]:
            user_preferences[user_id][event_type] = {}
        
        user_preferences[user_id][event_type]['enabled'] = enabled
        
        return {
            "message": f"Notification type {event_type} {'enabled' if enabled else 'disabled'}",
            "preferences": user_preferences[user_id]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
