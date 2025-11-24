"""
Test suite for documentation system
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns documentation links"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Quiz Platform API Documentation" in response.text
    assert "/api/docs" in response.text

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_metrics_endpoint():
    """Test metrics endpoint returns system statistics"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "avg_response_time_ms" in data
    assert "cache_hit_rate" in data

def test_openapi_schema():
    """Test OpenAPI schema is properly generated"""
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Quiz Platform API"
    assert schema["info"]["version"] == "1.0.0"
    assert "paths" in schema

def test_documentation_stats():
    """Test documentation statistics endpoint"""
    response = client.get("/api/documentation/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["coverage_percentage"] == 100.0
    assert data["total_endpoints"] > 0

def test_quiz_generation_documentation():
    """Test quiz generation endpoint has proper documentation"""
    response = client.get("/api/openapi.json")
    schema = response.json()
    
    # Check quiz generation endpoint exists and is documented
    assert "/api/v1/quiz/generate" in schema["paths"]
    endpoint = schema["paths"]["/api/v1/quiz/generate"]["post"]
    assert "summary" in endpoint
    assert "description" in endpoint
    assert "responses" in endpoint

def test_quiz_generation():
    """Test quiz generation with documentation"""
    response = client.post(
        "/api/v1/quiz/generate",
        json={
            "topic": "Python Programming",
            "difficulty": "medium",
            "num_questions": 3
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "quiz_id" in data
    assert len(data["questions"]) == 3
    assert "performance_ms" in data

def test_invalid_quiz_request():
    """Test validation error documentation"""
    response = client.post(
        "/api/v1/quiz/generate",
        json={
            "topic": "X",  # Too short
            "difficulty": "invalid",
            "num_questions": 100  # Too many
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
