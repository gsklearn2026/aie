import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import get_db, SessionLocal, engine
from app.models.learning_path import Base, User, Topic, UserProgress, LearningPath
import json
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown database for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create sample topics for testing
    db = SessionLocal()
    try:
        # Create some sample topics
        sample_topics = [
            Topic(
                id=1,
                name="Python Basics",
                description="Introduction to Python programming",
                difficulty_level=3.0,
                estimated_duration=120,
                prerequisites=[],
                learning_objectives=["Understand basic Python syntax", "Write simple programs"],
                content_type="video"
            ),
            Topic(
                id=2,
                name="Data Structures",
                description="Python data structures and algorithms",
                difficulty_level=5.0,
                estimated_duration=180,
                prerequisites=[1],
                learning_objectives=["Master Python data structures", "Implement algorithms"],
                content_type="interactive"
            ),
            Topic(
                id=3,
                name="Web Development",
                description="Building web applications with Python",
                difficulty_level=7.0,
                estimated_duration=240,
                prerequisites=[1, 2],
                learning_objectives=["Build web apps", "Use web frameworks"],
                content_type="project"
            ),
            Topic(
                id=4,
                name="Machine Learning",
                description="Introduction to ML with Python",
                difficulty_level=8.0,
                estimated_duration=300,
                prerequisites=[1, 2],
                learning_objectives=["Understand ML basics", "Implement ML algorithms"],
                content_type="interactive"
            )
        ]
        
        for topic in sample_topics:
            db.add(topic)
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Error setting up test data: {e}")
    finally:
        db.close()
    
    yield
    
    # Clean up after each test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Override database dependency for testing"""
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

def _generate_unique_username():
    """Generate unique username for testing"""
    return f"test_user_{uuid.uuid4().hex[:8]}"

def _generate_unique_email():
    """Generate unique email for testing"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def test_health_check():
    """Test API health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_user():
    """Test user creation endpoint"""
    user_data = {
        "username": _generate_unique_username(),
        "email": _generate_unique_email(),
        "learning_preferences": {"pace": "medium"}
    }
    
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["username"] == user_data["username"]

def test_generate_learning_path():
    """Test learning path generation endpoint"""
    # First create a user
    username = _generate_unique_username()
    email = _generate_unique_email()
    user_response = client.post("/api/users/", json={
        "username": username,
        "email": email
    })
    user_id = user_response.json()["user_id"]
    
    # Generate path
    path_request = {
        "user_id": user_id,
        "target_topics": [1, 2, 3],
        "max_difficulty_jump": 2.0
    }
    
    response = client.post("/api/learning-paths/generate", json=path_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "topic_sequence" in data
    assert "estimated_duration" in data
    assert data["user_id"] == user_id

def test_get_user_paths():
    """Test retrieving user's learning paths"""
    # Create user and path first
    username = _generate_unique_username()
    email = _generate_unique_email()
    user_response = client.post("/api/users/", json={
        "username": username,
        "email": email
    })
    user_id = user_response.json()["user_id"]
    
    # Generate a path
    client.post("/api/learning-paths/generate", json={
        "user_id": user_id,
        "target_topics": [1, 2]
    })
    
    # Get paths
    response = client.get(f"/api/learning-paths/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["user_id"] == user_id
    assert len(data["paths"]) > 0

def test_update_progress():
    """Test progress update endpoint"""
    # Create user
    username = _generate_unique_username()
    email = _generate_unique_email()
    user_response = client.post("/api/users/", json={
        "username": username,
        "email": email
    })
    user_id = user_response.json()["user_id"]
    
    # Update progress
    progress_data = {
        "topic_id": 1,
        "mastery_level": 0.8,
        "completion_status": "completed",
        "time_spent": 45
    }
    
    response = client.put(f"/api/learning-paths/{user_id}/progress", json=progress_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["user_id"] == user_id
    assert data["topic_id"] == 1

def test_get_next_topics():
    """Test next topics recommendation"""
    # Create user and generate path
    username = _generate_unique_username()
    email = _generate_unique_email()
    user_response = client.post("/api/users/", json={
        "username": username,
        "email": email
    })
    user_id = user_response.json()["user_id"]
    
    client.post("/api/learning-paths/generate", json={
        "user_id": user_id,
        "target_topics": [1, 2, 3, 4]
    })
    
    # Get recommendations
    response = client.get(f"/api/learning-paths/{user_id}/next-topics?count=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["recommendations"]) <= 2

def test_collaborative_path_generation():
    """Test collaborative filtering path generation"""
    username = _generate_unique_username()
    email = _generate_unique_email()
    user_response = client.post("/api/users/", json={
        "username": username,
        "email": email
    })
    user_id = user_response.json()["user_id"]
    
    path_request = {
        "user_id": user_id,
        "target_topics": [1, 2, 3],
        "use_collaborative": True
    }
    
    response = client.post("/api/learning-paths/generate", json=path_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "collaborative_insights" in data

def test_error_handling():
    """Test API error handling"""
    # Try to get non-existent user
    response = client.get("/api/users/99999")
    assert response.status_code == 404
    
    # Try invalid path generation with empty target topics
    response = client.post("/api/learning-paths/generate", json={
        "user_id": 99999,
        "target_topics": []
    })
    # Should return 400 Bad Request for validation error, not 500
    assert response.status_code in [400, 422]  # FastAPI validation error codes

if __name__ == "__main__":
    pytest.main([__file__])
