"""Tests for API integration layer"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.cache_service import CacheService
from app.services.ai_service import AIService

# Create a test client with proper service initialization
def create_test_client():
    """Create test client with initialized services"""
    test_app = app
    
    # Initialize services for testing
    cache_service = CacheService()
    ai_service = AIService()
    
    # Set services in app state
    test_app.state.cache_service = cache_service
    test_app.state.ai_service = ai_service
    
    return TestClient(test_app)

client = create_test_client()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_integration_health():
    """Test integration health endpoint"""
    response = client.get("/api/v1/integration/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_quiz_generation():
    """Test quiz generation endpoint"""
    response = client.post("/api/v1/quiz/generate?topic=Python&difficulty=easy&count=3")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3

def test_quiz_response_submission():
    """Test quiz response submission"""
    # First generate a quiz to get a question
    gen_response = client.post("/api/v1/quiz/generate?topic=Python&difficulty=easy&count=1")
    assert gen_response.status_code == 200
    
    quiz_data = gen_response.json()["data"][0]
    
    # Submit a response
    response_data = {
        "question_id": quiz_data["id"],
        "selected_answer": "A",
        "user_id": "test_user",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    response = client.post("/api/v1/quiz/submit", json=response_data)
    assert response.status_code == 200

def test_cache_operations():
    """Test cache operations"""
    # Clear cache
    response = client.post("/api/v1/integration/cache/clear")
    assert response.status_code == 200
    
    # Get metrics
    response = client.get("/api/v1/integration/metrics")
    assert response.status_code == 200
