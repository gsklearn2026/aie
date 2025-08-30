import pytest
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

@pytest.fixture
def sample_notification_data():
    """Sample notification data for testing"""
    return {
        "event_type": "quiz_completed",
        "user_id": "user123",
        "title": "Quiz Completed!",
        "message": "You completed the Python Basics quiz",
        "data": {"score": 85, "quiz_id": "quiz456"}
    }

@pytest.fixture
def sample_test_event():
    """Sample test event data for testing"""
    return {
        "event_type": "quiz_completed",
        "user_id": "user123",
        "quiz_id": "quiz456",
        "quiz_name": "Python Basics",
        "score": 85,
        "timestamp": "2025-05-15T10:30:00Z"
    }
