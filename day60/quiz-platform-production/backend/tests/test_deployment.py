import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Quiz Platform" in response.json()["service"]

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200

def test_readiness_check():
    response = client.get("/health/ready")
    # May fail in test environment without full services
    assert response.status_code in [200, 503]
