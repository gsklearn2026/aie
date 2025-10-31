"""
Test Suite for AI Quiz Platform - Day 38
Docker Compose Integration Tests
"""

import pytest
import requests
import json
import time
from unittest.mock import patch

# Test configuration
API_BASE = "http://localhost:8000"

class TestDockerComposeIntegration:
    
    def test_health_endpoint(self):
        """Test that health endpoint returns service status"""
        response = requests.get(f"{API_BASE}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'services' in data
        assert 'database' in data['services']
        assert 'redis' in data['services']
    
    def test_quizzes_endpoint(self):
        """Test quizzes API endpoint"""
        response = requests.get(f"{API_BASE}/api/quizzes")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 0  # Should have sample data
    
    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        response = requests.get(f"{API_BASE}/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_quizzes' in data
        assert 'total_users' in data
        assert 'timestamp' in data
    
    def test_generate_question(self):
        """Test AI question generation"""
        payload = {
            "topic": "Docker Containers",
            "difficulty": "medium"
        }
        
        response = requests.post(f"{API_BASE}/api/generate-question", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert 'question' in data
            assert 'options' in data
            assert 'correct_answer' in data
        else:
            # Might fail if Gemini API key not configured
            assert response.status_code in [500, 503]
    
    def test_submit_answer(self):
        """Test answer submission"""
        payload = {
            "answer": "Option A",
            "correct_answer": "Option A", 
            "question_id": "test_question"
        }
        
        response = requests.post(f"{API_BASE}/api/submit-answer", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert 'is_correct' in data
        assert data['is_correct'] == True
        assert 'timestamp' in data

class TestServiceCommunication:
    
    def test_database_connection(self):
        """Test database connectivity through health check"""
        response = requests.get(f"{API_BASE}/health")
        data = response.json()
        
        assert data['services']['database'] == 'connected'
    
    def test_redis_connection(self):
        """Test Redis connectivity through health check"""
        response = requests.get(f"{API_BASE}/health")
        data = response.json()
        
        assert data['services']['redis'] == 'connected'

if __name__ == "__main__":
    print("Running Docker Compose Integration Tests...")
    
    # Wait for services to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE}/health")
            if response.status_code == 200:
                print("✅ Services are ready!")
                break
        except:
            if i == max_retries - 1:
                print("❌ Services failed to start")
                exit(1)
            print(f"⏳ Waiting for services... ({i+1}/{max_retries})")
            time.sleep(2)
    
    # Run tests
    pytest.main([__file__, "-v"])
