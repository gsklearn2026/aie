import pytest
import json
import time
from backend.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['REDIS_URL'] = 'redis://localhost:6379/1'  # Use test database
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_rate_limit_endpoint_protection(client):
    """Test that endpoints are protected by rate limiting"""
    
    # Make multiple requests quickly
    responses = []
    for i in range(12):  # Exceed admin limit of 10/minute
        response = client.get('/api/rate-limit/status', headers={'X-User-ID': 'test_user'})
        responses.append(response)
        
    # Check that some requests were rate limited
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes  # Rate limit exceeded

def test_quiz_generation_rate_limit(client):
    """Test AI generation endpoint rate limiting"""
    
    # Mock Gemini API key
    with client.application.app_context():
        client.application.config['GEMINI_API_KEY'] = 'test_key'
    
    # Make requests to AI generation endpoint
    quiz_data = {
        'topic': 'Test Topic',
        'difficulty': 'easy',
        'num_questions': 3
    }
    
    responses = []
    for i in range(7):  # Exceed AI generation limit of 5/minute
        response = client.post('/api/quiz/generate', 
                              json=quiz_data,
                              headers={'X-User-ID': 'test_user'})
        responses.append(response)
        time.sleep(0.1)  # Small delay between requests
    
    # Check rate limiting kicks in
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes

def test_tier_upgrade_functionality(client):
    """Test user tier upgrade functionality"""
    
    # Upgrade user tier
    upgrade_data = {
        'user_id': 'test_user',
        'tier': 'premium'
    }
    
    response = client.post('/api/rate-limit/upgrade-tier', json=upgrade_data)
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'premium' in data['message']

def test_rate_limit_headers(client):
    """Test that rate limit headers are included in responses"""
    
    response = client.get('/api/rate-limit/status', headers={'X-User-ID': 'test_user'})
    
    # Check for rate limit headers
    assert 'X-RateLimit-Limit' in response.headers
    assert 'X-RateLimit-Remaining' in response.headers
    assert 'X-RateLimit-Reset' in response.headers

def test_redis_integration(client):
    """Test Redis integration for rate limiting"""
    
    # Make a request
    response = client.get('/api/rate-limit/status', headers={'X-User-ID': 'redis_test_user'})
    assert response.status_code == 200
    
    # Check that data is stored in Redis
    with client.application.app_context():
        redis_client = client.application.redis
        
        # Check for rate limit keys
        keys = redis_client.keys('bucket:*redis_test_user*')
        assert len(keys) > 0
