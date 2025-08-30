import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
from backend.app.main import app

client = TestClient(app)

class TestNotificationsAPI:
    """Test cases for the notifications API endpoints"""
    
    @patch('backend.app.api.notifications.redis_client')
    def test_send_notification_success(self, mock_redis):
        """Test successful notification sending"""
        notification_data = {
            "event_type": "quiz_completed",
            "user_id": "user123",
            "title": "Quiz Completed!",
            "message": "You completed the Python Basics quiz",
            "data": {"score": 85, "quiz_id": "quiz456"}
        }
        
        mock_redis.rpush.return_value = 1
        
        response = client.post("/api/notifications/send", json=notification_data)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Notification queued successfully"
        mock_redis.rpush.assert_called_once()
    
    @patch('backend.app.api.notifications.redis_client')
    def test_send_notification_redis_error(self, mock_redis):
        """Test notification sending when Redis fails"""
        notification_data = {
            "event_type": "quiz_completed",
            "user_id": "user123",
            "title": "Quiz Completed!",
            "message": "You completed the Python Basics quiz",
            "data": {"score": 85, "quiz_id": "quiz456"}
        }
        
        mock_redis.rpush.side_effect = Exception("Redis connection failed")
        
        response = client.post("/api/notifications/send", json=notification_data)
        
        assert response.status_code == 500
        assert "Redis connection failed" in response.json()["detail"]
    
    @patch('backend.app.api.notifications.redis_client')
    def test_create_test_event(self, mock_redis):
        """Test creating a test notification event"""
        mock_redis.rpush.return_value = 1
        
        response = client.post("/api/notifications/test-event")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Test event created"
        assert "event" in response.json()
        
        # Verify the test event structure
        test_event = response.json()["event"]
        assert test_event["event_type"] == "quiz_completed"
        assert test_event["user_id"] == "user123"
        assert test_event["quiz_id"] == "quiz456"
        assert test_event["quiz_name"] == "Python Basics"
        assert test_event["score"] == 85
        
        mock_redis.rpush.assert_called_once()
    
    @patch('backend.app.api.notifications.notification_service')
    def test_get_user_notifications_success(self, mock_notification_service):
        """Test getting user notifications successfully"""
        mock_notifications = [
            {"id": 1, "title": "Quiz Completed", "message": "Great job!"},
            {"id": 2, "title": "New Course", "message": "Check out this course"}
        ]
        mock_notification_service.get_user_notifications.return_value = mock_notifications
        
        response = client.get("/api/notifications/user/user123?limit=10")
        
        assert response.status_code == 200
        assert response.json()["notifications"] == mock_notifications
        mock_notification_service.get_user_notifications.assert_called_once_with("user123", 10)
    
    @patch('backend.app.api.notifications.notification_service')
    def test_get_user_notifications_service_error(self, mock_notification_service):
        """Test getting user notifications when service fails"""
        mock_notification_service.get_user_notifications.side_effect = Exception("Service error")
        
        response = client.get("/api/notifications/user/user123")
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]
