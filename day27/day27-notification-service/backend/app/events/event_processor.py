import asyncio
import json
import logging
from typing import Dict, Any
from ..services.notification_service import NotificationService
from ..services.preference_service import PreferenceService

logger = logging.getLogger(__name__)

class EventProcessor:
    def __init__(self, redis_client, websocket_manager):
        self.redis = redis_client
        self.websocket_manager = websocket_manager
        self.notification_service = NotificationService(websocket_manager)
        self.preference_service = PreferenceService()
        self.running = False
        
    async def start_processing(self):
        """Start processing events from Redis queue"""
        self.running = True
        logger.info("Event processor started")
        
        # Add a small delay to allow startup to complete
        await asyncio.sleep(0.1)
        
        while self.running:
            try:
                # Check for events in Redis list with shorter timeout
                event_data = self.redis.blpop(['notification_events'], timeout=0.1)
                if event_data:
                    _, event_json = event_data
                    event = json.loads(event_json)
                    await self.process_event(event)
                else:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                await asyncio.sleep(1)
    
    async def process_event(self, event: Dict[str, Any]):
        """Process a single event"""
        try:
            event_type = event.get('event_type')
            user_id = event.get('user_id')
            
            logger.info(f"Processing {event_type} event for user {user_id}")
            
            # Check user preferences
            preferences = await self.preference_service.get_user_preferences(user_id)
            
            if self.should_send_notification(event_type, preferences):
                await self.notification_service.send_notification(event)
                
        except Exception as e:
            logger.error(f"Error processing event {event}: {e}")
    
    def should_send_notification(self, event_type: str, preferences: Dict) -> bool:
        """Check if notification should be sent based on user preferences"""
        if not preferences:
            return True  # Default to send if no preferences set
            
        return preferences.get(event_type, {}).get('enabled', True)
    
    def stop(self):
        """Stop the event processor"""
        self.running = False
        logger.info("Event processor stopped")
