from typing import Dict, Any, Optional

class PreferenceService:
    def __init__(self):
        # In-memory storage for demo
        self.preferences: Dict[str, Dict[str, Any]] = {}
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        return self.preferences.get(user_id, {
            'quiz_completed': {'enabled': True},
            'quiz_created': {'enabled': True},
            'system_update': {'enabled': True}
        })
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user notification preferences"""
        self.preferences[user_id] = preferences
        return preferences
