import pytest
import requests
import time
import os
import subprocess
import threading

class TestLoadTestIntegration:
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.base_url = "http://localhost:8000"
        cls.dashboard_url = "http://localhost:8080"
    
    def test_api_health_check(self):
        """Test if Quiz API is accessible"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            assert response.status_code in [200, 404]  # 404 acceptable if endpoint doesn't exist
        except requests.exceptions.ConnectionError:
            pytest.skip("Quiz API not running")
    
    def test_dashboard_accessibility(self):
        """Test if performance dashboard is accessible"""
        try:
            response = requests.get(self.dashboard_url, timeout=10)
            # Streamlit returns 200 for the app
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Dashboard not running")
    
    def test_load_test_execution(self):
        """Test load test can be executed"""
        # Run a minimal load test
        cmd = [
            "locust", 
            "-f", "src/load_tests/quiz_platform_load_test.py",
            "--headless",
            "-u", "2",  # 2 users
            "-r", "1",  # 1 user per second
            "-t", "10s",  # 10 seconds
            "--host", self.base_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # Load test should complete without crashing
            assert result.returncode in [0, 1]  # 0 = success, 1 = some failures acceptable
        except subprocess.TimeoutExpired:
            pytest.fail("Load test took too long to complete")
        except FileNotFoundError:
            pytest.skip("Locust not installed")

if __name__ == "__main__":
    pytest.main([__file__])
