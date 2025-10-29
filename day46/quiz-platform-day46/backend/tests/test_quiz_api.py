import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_start_quiz():
    response = client.post("/api/quiz/start", json={
        "quiz_id": "test-quiz",
        "user_id": "test-user",
        "quiz_title": "Test Quiz"
    })
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["total_questions"] > 0
    return data["session_id"]

def test_quiz_flow():
    # Start quiz
    start_response = client.post("/api/quiz/start", json={
        "quiz_id": "test-quiz",
        "user_id": "test-user",
        "quiz_title": "Test Quiz"
    })
    session_id = start_response.json()["session_id"]
    
    # Get session
    session_response = client.get(f"/api/quiz/session/{session_id}")
    assert session_response.status_code == 200
    session_data = session_response.json()
    assert session_data["status"] == "active"
    
    # Submit answer
    question = session_data["current_question"]
    answer_response = client.post(f"/api/quiz/session/{session_id}/answer", json={
        "question_id": question["id"],
        "answer": question["options"][0],
        "time_taken": 10.0
    })
    assert answer_response.status_code == 200
