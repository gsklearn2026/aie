import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Question Difficulty Classification" in response.text

def test_classify_endpoint():
    question_data = {
        "question_text": "What is the capital of France?",
        "subject": "geography", 
        "question_type": "multiple_choice"
    }
    
    response = client.post("/api/v1/classify", json=question_data)
    assert response.status_code == 200
    
    result = response.json()
    assert "difficulty_level" in result
    assert "difficulty_score" in result
    assert "confidence" in result
    assert "processing_time_ms" in result

def test_classify_invalid_input():
    invalid_data = {
        "question_text": "",  # Empty text
        "subject": "geography",
        "question_type": "multiple_choice"
    }
    
    response = client.post("/api/v1/classify", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_batch_classification():
    batch_data = {
        "questions": [
            {
                "question_text": "What is 2 + 2?",
                "subject": "mathematics",
                "question_type": "multiple_choice"
            },
            {
                "question_text": "Explain quantum entanglement.",
                "subject": "physics", 
                "question_type": "essay"
            }
        ]
    }
    
    response = client.post("/api/v1/classify-batch", json=batch_data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["total_processed"] == 2
    assert len(result["results"]) == 2
    assert result["average_processing_time_ms"] > 0

def test_features_endpoint():
    params = {
        "question_text": "What is the capital of France?",
        "question_type": "multiple_choice",
        "subject": "geography"
    }
    
    response = client.get("/api/v1/features/test", params=params)
    assert response.status_code == 200
    
    result = response.json()
    assert "features" in result
    assert "question_text" in result
