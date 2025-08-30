import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from backend.app.main import app

client = TestClient(app)

class TestMainApp:
    """Test cases for the main application endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Notification Service API"
        assert response.json()["status"] == "running"
    
    @patch('backend.app.main.redis_client')
    def test_health_check_healthy(self, mock_redis):
        """Test health check when Redis is healthy"""
        mock_redis.ping.return_value = True
        
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["redis"] == "connected"
        mock_redis.ping.assert_called_once()
    
    @patch('backend.app.main.redis_client')
    def test_health_check_unhealthy(self, mock_redis):
        """Test health check when Redis is unhealthy"""
        mock_redis.ping.side_effect = Exception("Connection refused")
        
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "unhealthy"
        assert "Connection refused" in response.json()["error"]
