import pytest
import json
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_swagger_json_endpoint(client):
    """Test OpenAPI specification endpoint"""
    response = client.get('/swagger.json')
    assert response.status_code == 200
    spec = json.loads(response.data)
    assert 'openapi' in spec or 'swagger' in spec
    assert 'info' in spec
    assert spec['info']['title'] == 'Quiz Platform API'

def test_swagger_ui_endpoint(client):
    """Test Swagger UI documentation endpoint"""
    response = client.get('/docs/')
    assert response.status_code == 200
    assert b'swagger-ui' in response.data.lower()

def test_api_endpoints_documented(client):
    """Verify all main endpoints are documented"""
    response = client.get('/swagger.json')
    spec = json.loads(response.data)
    paths = spec['paths']
    
    # Check key endpoints exist in documentation
    assert '/api/v1/quizzes/' in paths
    assert '/api/v1/users/' in paths
    assert '/api/v1/analytics/stats' in paths
    assert '/health' in paths

def test_model_schemas_defined(client):
    """Verify data models are properly defined"""
    response = client.get('/swagger.json')
    spec = json.loads(response.data)
    
    if 'definitions' in spec:
        models = spec['definitions']
    elif 'components' in spec and 'schemas' in spec['components']:
        models = spec['components']['schemas']
    else:
        models = {}
    
    # Check required models exist
    assert 'Quiz' in models
    assert 'User' in models
    assert 'QuizResult' in models

def test_quiz_operations(client):
    """Test quiz CRUD operations work correctly"""
    # Test GET /api/v1/quizzes/
    response = client.get('/api/v1/quizzes/')
    assert response.status_code == 200
    
    # Test POST /api/v1/quizzes/
    quiz_data = {
        'title': 'Test Quiz',
        'description': 'Test Description',
        'difficulty': 'easy',
        'category': 'Test',
        'questions': []
    }
    response = client.post('/api/v1/quizzes/', 
                          json=quiz_data,
                          content_type='application/json')
    assert response.status_code == 201

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'services' in data

def test_analytics_endpoints(client):
    """Test analytics endpoints are accessible"""
    response = client.get('/api/v1/analytics/stats')
    assert response.status_code == 200
    
    response = client.get('/api/v1/analytics/results')
    assert response.status_code == 200

def test_ai_endpoints(client):
    """Test AI generation endpoints"""
    response = client.post('/api/v1/ai/generate-questions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'questions' in data
    assert 'generated_at' in data
