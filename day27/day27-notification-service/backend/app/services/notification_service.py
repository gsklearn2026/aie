import asyncio
import json
import redis
from typing import Dict, Any, List
from ..models.notification import Notification, NotificationStatus
from .email_service import EmailService
from .websocket_manager import WebSocketManager
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.email_service = EmailService()
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    async def send_notification(self, event: Dict[str, Any]):
        """Send notification based on event data"""
        try:
            user_id = event.get('user_id')
            event_type = event.get('event_type')
            
            # Create notification object
            notification = Notification(
                user_id=user_id,
                event_type=event_type,
                title=self.generate_title(event),
                message=self.generate_message(event),
                data=event
            )
            
            # Store notification in Redis
            self.store_notification(notification)
            
            # Send via multiple channels
            await self.send_realtime_notification(notification)
            await self.send_email_notification(notification)
            
            notification.status = NotificationStatus.SENT
            logger.info(f"Notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            if 'notification' in locals():
                notification.status = NotificationStatus.FAILED
    
    def store_notification(self, notification: Notification):
        """Store notification in Redis"""
        try:
            notification_data = {
                "id": str(notification.id),
                "user_id": notification.user_id,
                "event_type": notification.event_type,
                "title": notification.title,
                "message": notification.message,
                "status": notification.status.value,
                "created_at": notification.created_at.isoformat(),
                "data": notification.data
            }
            
            # Store in user's notification list
            user_key = f"user_notifications:{notification.user_id}"
            self.redis_client.lpush(user_key, json.dumps(notification_data))
            
            # Keep only last 100 notifications per user
            self.redis_client.ltrim(user_key, 0, 99)
            
            # Store in global notifications list
            global_key = "all_notifications"
            self.redis_client.lpush(global_key, json.dumps(notification_data))
            self.redis_client.ltrim(global_key, 0, 999)
            
        except Exception as e:
            logger.error(f"Failed to store notification: {e}")
    
    async def send_realtime_notification(self, notification: Notification):
        """Send real-time notification via WebSocket"""
        try:
            message = {
                "type": "notification",
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "timestamp": notification.created_at.isoformat(),
                "event_type": notification.event_type
            }
            
            await self.websocket_manager.send_to_user(
                notification.user_id, 
                json.dumps(message)
            )
            
        except Exception as e:
            logger.error(f"Failed to send real-time notification: {e}")
    
    async def send_email_notification(self, notification: Notification):
        """Send email notification"""
        try:
            await self.email_service.send_email(
                to_email=f"user{notification.user_id}@example.com",
                subject=notification.title,
                body=notification.message
            )
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def generate_title(self, event: Dict[str, Any]) -> str:
        """Generate notification title based on event"""
        event_type = event.get('event_type')
        
        titles = {
            'quiz_completed': 'Quiz Completed!',
            'quiz_created': 'New Quiz Available',
            'quiz_result': 'Your Quiz Results',
            'system_update': 'System Update'
        }
        
        return titles.get(event_type, 'Notification')
    
    def generate_message(self, event: Dict[str, Any]) -> str:
        """Generate notification message based on event"""
        event_type = event.get('event_type')
        
        if event_type == 'quiz_completed':
            score = event.get('score', 0)
            quiz_name = event.get('quiz_name', 'Quiz')
            return f"You completed {quiz_name} with a score of {score}%!"
        
        elif event_type == 'quiz_created':
            quiz_name = event.get('quiz_name', 'Quiz')
            return f"New quiz '{quiz_name}' is now available!"
        
        return "You have a new notification"
    
    def get_user_notifications(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get notifications for a user from Redis"""
        try:
            user_key = f"user_notifications:{user_id}"
            notifications_data = self.redis_client.lrange(user_key, 0, limit - 1)
            
            notifications = []
            for notification_json in notifications_data:
                try:
                    notification = json.loads(notification_json)
                    notifications.append(notification)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse notification JSON: {notification_json}")
                    continue
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
