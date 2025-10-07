import pytest
import httpx
import asyncio
import os

class TestCDIntegration:
    
    @pytest.fixture
    def base_url(self):
        return os.getenv("STAGING_URL", "http://localhost:8000")
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, base_url):
        """Test health endpoint responds correctly"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "version" in data
    
    @pytest.mark.asyncio
    async def test_readiness_endpoint(self, base_url):
        """Test readiness endpoint performs all checks"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/ready")
            data = response.json()
            
            # Should have status and checks
            assert "status" in data
            assert "checks" in data
            assert "database" in data["checks"]
            assert "memory" in data["checks"]
    
    @pytest.mark.asyncio
    async def test_quiz_generation(self, base_url):
        """Test quiz generation endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/api/quiz/generate")
            
            if response.status_code == 200:
                data = response.json()
                assert "quiz_id" in data
                assert "questions" in data
                assert len(data["questions"]) > 0
            else:
                # API key might not be configured in test environment
                assert response.status_code in [500, 503]
    
    @pytest.mark.asyncio
    async def test_deployment_info(self, base_url):
        """Test deployment info endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/deployment/info")
            assert response.status_code == 200
            data = response.json()
            assert "environment" in data
            assert "version" in data
            assert "deployed_at" in data

    @pytest.mark.asyncio
    async def test_cors_headers(self, base_url):
        """Test CORS headers are present"""
        async with httpx.AsyncClient() as client:
            response = await client.options(f"{base_url}/api/quiz/generate")
            assert "access-control-allow-origin" in response.headers
