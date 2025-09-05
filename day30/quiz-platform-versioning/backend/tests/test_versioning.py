import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_version_detection_url():
    """Test version detection from URL path"""
    response = client.post("/api/v1/quiz/create", json={
        "title": "Test Quiz",
        "description": "Test Description",
        "questions": [{
            "question": "Test question?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 0,
            "points": 1
        }]
    })
    assert response.status_code == 200
    assert response.headers.get("X-API-Version") == "v1"

def test_v1_quiz_creation():
    """Test V1 quiz creation without AI features"""
    quiz_data = {
        "title": "V1 Test Quiz",
        "description": "Testing V1 API",
        "questions": [{
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1,
            "points": 1
        }]
    }
    
    response = client.post("/api/v1/quiz/create", json=quiz_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == quiz_data["title"]
    assert "ai_difficulty_score" not in data  # V1 shouldn't have AI features

def test_v2_quiz_creation():
    """Test V2 quiz creation with AI enhancements"""
    quiz_data = {
        "title": "V2 Test Quiz",
        "description": "Testing V2 API with AI",
        "questions": [{
            "question": "Explain the concept of API versioning in software development",
            "options": ["A simple technique", "A complex strategy", "A backward compatibility approach", "All of the above"],
            "correct_answer": 3,
            "points": 1
        }]
    }
    
    response = client.post("/api/v2/quiz/create", json=quiz_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == quiz_data["title"]
    assert "ai_difficulty_score" in data  # V2 should have AI features
    assert "ai_tags" in data
    assert "estimated_duration" in data

def test_backward_compatibility():
    """Test that v1 quizzes are accessible via v2 with AI enhancements"""
    # Create quiz via v1
    v1_quiz = {
        "title": "V1 Original Quiz",
        "description": "Created with V1 API",
        "questions": [{
            "question": "Simple question",
            "options": ["A", "B"],
            "correct_answer": 0,
            "points": 1
        }]
    }
    
    v1_response = client.post("/api/v1/quiz/create", json=v1_quiz)
    quiz_id = v1_response.json()["id"]
    
    # Access via v2 - should have AI enhancements
    v2_response = client.get(f"/api/v2/quiz/{quiz_id}")
    assert v2_response.status_code == 200
    v2_data = v2_response.json()
    assert "ai_difficulty_score" in v2_data
    assert "ai_tags" in v2_data

def test_version_analytics():
    """Test version analytics endpoint"""
    response = client.get("/api/version/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "version_distribution" in data
    assert "daily_stats" in data
    assert "endpoint_popularity" in data

def test_v2_analytics_endpoint():
    """Test V2 exclusive analytics endpoint"""
    # Create a quiz first
    quiz_data = {
        "title": "Analytics Test Quiz",
        "description": "For testing analytics",
        "questions": [
            {
                "question": "Easy question",
                "options": ["A", "B"],
                "correct_answer": 0,
                "points": 1
            },
            {
                "question": "This is a much more complex and difficult question that requires deeper thinking",
                "options": ["Complex A", "Complex B", "Complex C", "Complex D"],
                "correct_answer": 2,
                "points": 2
            }
        ]
    }
    
    create_response = client.post("/api/v2/quiz/create", json=quiz_data)
    quiz_id = create_response.json()["id"]
    
    # Test analytics endpoint
    analytics_response = client.get(f"/api/v2/quiz/{quiz_id}/analytics")
    assert analytics_response.status_code == 200
    analytics_data = analytics_response.json()
    
    assert "difficulty_distribution" in analytics_data
    assert "cognitive_load_distribution" in analytics_data
    assert analytics_data["total_questions"] == 2

def test_deprecation_headers():
    """Test that V1 endpoints return deprecation headers"""
    response = client.get("/api/v1/quiz/list")
    assert response.headers.get("X-API-Deprecated") == "True"
    
    response = client.get("/api/v2/quiz/list")
    assert response.headers.get("X-API-Deprecated") == "False"
