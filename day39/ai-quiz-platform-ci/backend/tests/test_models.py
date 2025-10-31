import pytest
from app.models import Quiz, UserResponse
from app.database import Base, engine

def test_quiz_model():
    # Test model creation
    quiz = Quiz(topic="Math", difficulty="easy", questions="[]")
    assert quiz.topic == "Math"
    assert quiz.difficulty == "easy"
    assert quiz.is_active is None  # Not set until saved

def test_user_response_model():
    response = UserResponse(quiz_id=1, user_id="test", answers="[]", score=80)
    assert response.quiz_id == 1
    assert response.score == 80
