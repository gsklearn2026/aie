import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Quiz Platform" in response.json()["message"]

def test_create_quiz_job():
    """Test creating a quiz generation job"""
    job_data = {
        "topic": "Python Programming",
        "num_questions": 5,
        "difficulty": "medium"
    }
    
    response = client.post("/api/v1/jobs/generate-quiz", json=job_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "Python Programming" in data["message"]

def test_create_batch_job():
    """Test creating a batch quiz job"""
    job_data = {
        "topics": ["JavaScript", "React", "Node.js"],
        "num_questions_per_topic": 3
    }
    
    response = client.post("/api/v1/jobs/batch-quiz", json=job_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "3 topics" in data["message"]

def test_list_jobs():
    """Test listing jobs"""
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_job_stats():
    """Test job statistics endpoint"""
    response = client.get("/api/v1/jobs/stats/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "queue_length" in data
