import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.app.models.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_quiz():
    # First register/login a user
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create a quiz
    quiz_data = {
        "title": "Test Quiz",
        "description": "A test quiz",
        "questions": [
            {
                "text": "What is 2+2?",
                "type": "multiple_choice",
                "options": ["3", "4", "5"],
                "correct_answer": "4"
            }
        ]
    }
    
    response = client.post(
        "/api/quiz/",
        json=quiz_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Quiz"

def test_get_quizzes():
    response = client.post("/api/auth/register", json={
        "email": "test2@example.com",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    
    response = client.get(
        "/api/quiz/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
