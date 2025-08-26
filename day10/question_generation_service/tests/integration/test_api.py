"""Integration tests for question generation service"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.question_service.api.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    with patch("src.question_service.api.main.redis_client") as mock_redis:
        mock_redis.ping = AsyncMock(return_value=True)

        response = client.get("/health")

        assert response.status_code == 200
        assert "healthy" in response.json()["status"]


def test_generate_questions_endpoint(client):
    """Test question generation endpoint"""
    with patch("src.question_service.api.main.job_manager") as mock_manager:
        mock_manager.create_job = AsyncMock(return_value=True)

        response = client.post(
            "/questions/generate",
            json={"topic": "Python programming", "count": 5, "difficulty": "medium"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"


def test_get_job_status_endpoint(client):
    """Test job status endpoint"""
    with patch("src.question_service.api.main.job_manager") as mock_manager:
        mock_manager.get_job = AsyncMock(
            return_value={"job_id": "test-123", "status": "completed", "questions": []}
        )

        response = client.get("/questions/jobs/test-123")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-123"
        assert data["status"] == "completed"


def test_get_job_not_found(client):
    """Test job not found"""
    with patch("src.question_service.api.main.job_manager") as mock_manager:
        mock_manager.get_job = AsyncMock(return_value=None)

        response = client.get("/questions/jobs/nonexistent")

        assert response.status_code == 404
