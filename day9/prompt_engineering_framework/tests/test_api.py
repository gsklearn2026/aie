"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app

@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)

class TestAPI:
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        assert "Prompt Engineering Framework API" in response.json()["message"]
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_and_get_template(self, client):
        """Test template creation and retrieval via API"""
        template_data = {
            "metadata": {
                "name": "api_test_template",
                "description": "Template created via API"
            },
            "prompt": "API test: {message}",
            "variables": {
                "message": {
                    "type": "string",
                    "required": True
                }
            }
        }
        
        # Create template
        response = client.post("/api/v1/templates", json=template_data)
        assert response.status_code == 201
        
        # Get template
        response = client.get("/api/v1/templates/api_test_template")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["name"] == "api_test_template"
    
    def test_render_template_via_api(self, client):
        """Test template rendering via API"""
        # First create a template
        template_data = {
            "metadata": {"name": "render_api_test"},
            "prompt": "Hello {name}!",
            "variables": {
                "name": {"type": "string", "required": True}
            }
        }
        
        client.post("/api/v1/templates", json=template_data)
        
        # Then render it
        variables = {"name": "API User"}
        response = client.post(
            "/api/v1/templates/render_api_test/render",
            json=variables
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Hello API User!" in data["rendered_prompt"]
    
    def test_list_templates_api(self, client):
        """Test listing templates via API"""
        response = client.get("/api/v1/templates")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
