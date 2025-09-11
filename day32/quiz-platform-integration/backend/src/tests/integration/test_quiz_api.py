import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app
from models.database import engine, Base
import os

# Set test database URL
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost/test_quizdb"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def setup_database():
    """Create test database tables before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestQuizAPI:
    
    async def test_health_check(self, client: AsyncClient):
        """Test API health endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_create_quiz(self, client: AsyncClient, setup_database):
        """Test quiz creation endpoint."""
        quiz_data = {
            "title": "Python Basics",
            "description": "Basic Python programming concepts",
            "creator_id": 1
        }
        
        response = await client.post("/api/quiz/", json=quiz_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["title"] == quiz_data["title"]
        assert result["description"] == quiz_data["description"]
        assert "id" in result
        assert "created_at" in result

    async def test_get_quiz(self, client: AsyncClient, setup_database):
        """Test quiz retrieval endpoint."""
        # First create a quiz
        quiz_data = {
            "title": "JavaScript Fundamentals",
            "description": "Core JavaScript concepts",
            "creator_id": 1
        }
        
        create_response = await client.post("/api/quiz/", json=quiz_data)
        quiz_id = create_response.json()["id"]
        
        # Then retrieve it
        response = await client.get(f"/api/quiz/{quiz_id}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["title"] == quiz_data["title"]
        assert result["id"] == quiz_id

    async def test_get_nonexistent_quiz(self, client: AsyncClient, setup_database):
        """Test retrieving non-existent quiz returns 404."""
        response = await client.get("/api/quiz/9999")
        assert response.status_code == 404

    async def test_generate_questions_for_quiz(self, client: AsyncClient, setup_database):
        """Test question generation for existing quiz."""
        # Create quiz first
        quiz_data = {
            "title": "Math Quiz",
            "description": "Basic mathematics",
            "creator_id": 1
        }
        
        create_response = await client.post("/api/quiz/", json=quiz_data)
        quiz_id = create_response.json()["id"]
        
        # Generate questions
        questions_data = {
            "topic": "basic algebra",
            "count": 3
        }
        
        response = await client.post(f"/api/quiz/{quiz_id}/questions", json=questions_data)
        assert response.status_code == 200
        assert "Added 3 questions" in response.json()["message"]

    async def test_delete_quiz(self, client: AsyncClient, setup_database):
        """Test quiz deletion."""
        # Create quiz first
        quiz_data = {
            "title": "Temp Quiz",
            "description": "To be deleted",
            "creator_id": 1
        }
        
        create_response = await client.post("/api/quiz/", json=quiz_data)
        quiz_id = create_response.json()["id"]
        
        # Delete quiz
        response = await client.delete(f"/api/quiz/{quiz_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify it's gone
        get_response = await client.get(f"/api/quiz/{quiz_id}")
        assert get_response.status_code == 404

class TestAuthAPI:
    
    async def test_user_registration(self, client: AsyncClient, setup_database):
        """Test user registration endpoint."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["username"] == user_data["username"]
        assert result["email"] == user_data["email"]
        assert "id" in result
        assert result["is_active"] is True

    async def test_get_user(self, client: AsyncClient, setup_database):
        """Test user retrieval."""
        # Register user first
        user_data = {
            "username": "getuser",
            "email": "get@example.com",
            "password": "getpass123"
        }
        
        register_response = await client.post("/api/auth/register", json=user_data)
        user_id = register_response.json()["id"]
        
        # Get user
        response = await client.get(f"/api/auth/users/{user_id}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["id"] == user_id
        assert result["username"] == user_data["username"]

    async def test_duplicate_email_registration(self, client: AsyncClient, setup_database):
        """Test duplicate email registration fails."""
        user_data = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "pass123"
        }
        
        # First registration should succeed
        response1 = await client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration with same email should fail
        user_data["username"] = "user2"
        response2 = await client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]

class TestIntegrationWorkflows:
    
    async def test_complete_quiz_creation_workflow(self, client: AsyncClient, setup_database):
        """Test complete workflow: user registration -> quiz creation -> question generation."""
        # 1. Register user
        user_data = {
            "username": "quizmaster",
            "email": "quizmaster@example.com",
            "password": "masterpass123"
        }
        
        user_response = await client.post("/api/auth/register", json=user_data)
        user_id = user_response.json()["id"]
        
        # 2. Create quiz
        quiz_data = {
            "title": "Complete Workflow Test",
            "description": "End-to-end integration test",
            "creator_id": user_id
        }
        
        quiz_response = await client.post("/api/quiz/", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        # 3. Generate questions
        questions_data = {
            "topic": "integration testing",
            "count": 2
        }
        
        questions_response = await client.post(
            f"/api/quiz/{quiz_id}/questions", 
            json=questions_data
        )
        assert questions_response.status_code == 200
        
        # 4. Verify complete quiz
        final_quiz = await client.get(f"/api/quiz/{quiz_id}")
        result = final_quiz.json()
        
        assert result["title"] == quiz_data["title"]
        assert result["creator_id"] == user_id
        assert "questions" in result
        assert len(result["questions"]) == 2
