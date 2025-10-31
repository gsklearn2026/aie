import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code in [200, 503]

def test_generate_quiz():
    response = client.post("/api/quiz/generate?topic=Python&difficulty=easy&num_questions=3")
    if response.status_code == 200:
        data = response.json()
        assert "quiz_id" in data
        assert "quiz" in data
        assert len(data["quiz"]["questions"]) == 3

def test_quiz_not_found():
    response = client.get("/api/quiz/nonexistent")
    assert response.status_code == 404
