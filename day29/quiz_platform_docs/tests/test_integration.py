import pytest
import requests
import time
import json

BASE_URL = 'http://localhost:5000'

def test_full_api_workflow():
    """Test complete API workflow"""
    # Test health check
    response = requests.get(f'{BASE_URL}/health')
    assert response.status_code == 200
    
    # Create a quiz
    quiz_data = {
        'title': 'Integration Test Quiz',
        'description': 'Test quiz for integration testing',
        'difficulty': 'medium',
        'category': 'Testing',
        'questions': [
            {
                'text': 'What is API testing?',
                'options': ['Testing APIs', 'Testing UI', 'Testing DB', 'Testing Networks'],
                'correct_answer': 'Testing APIs'
            }
        ]
    }
    
    response = requests.post(f'{BASE_URL}/api/v1/quizzes/', json=quiz_data)
    assert response.status_code == 201
    quiz = response.json()
    quiz_id = quiz['id']
    
    # Retrieve the quiz
    response = requests.get(f'{BASE_URL}/api/v1/quizzes/{quiz_id}')
    assert response.status_code == 200
    retrieved_quiz = response.json()
    assert retrieved_quiz['title'] == quiz_data['title']
    
    # Update the quiz
    update_data = {'title': 'Updated Integration Test Quiz'}
    response = requests.put(f'{BASE_URL}/api/v1/quizzes/{quiz_id}', json=update_data)
    assert response.status_code == 200
    
    # Test analytics
    response = requests.get(f'{BASE_URL}/api/v1/analytics/stats')
    assert response.status_code == 200
    stats = response.json()
    assert 'total_quizzes' in stats
    
    # Clean up - delete the quiz
    response = requests.delete(f'{BASE_URL}/api/v1/quizzes/{quiz_id}')
    assert response.status_code == 204

def test_documentation_accessibility():
    """Test that documentation is accessible"""
    # Test Swagger UI
    response = requests.get(f'{BASE_URL}/docs/')
    assert response.status_code == 200
    
    # Test OpenAPI spec
    response = requests.get(f'{BASE_URL}/swagger.json')
    assert response.status_code == 200
    spec = response.json()
    assert 'info' in spec
    assert spec['info']['title'] == 'Quiz Platform API'
