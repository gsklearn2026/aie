import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.config.manager import ConfigManager

class TestConfigManager:
    
    def test_default_environment(self):
        """Test default environment selection"""
        config = ConfigManager()
        assert config.env == 'development'
    
    @patch.dict(os.environ, {'APP_ENV': 'production', 'GEMINI_API_KEY': 'test-key'})
    def test_environment_from_env_var(self):
        """Test environment from environment variable"""
        config = ConfigManager()
        assert config.env == 'production'
    
    def test_config_loading(self):
        """Test configuration loading"""
        config = ConfigManager('development')
        assert config.get('app.name') == 'AI Quiz Platform'
        assert config.get('app.debug') == True  # Development override
    
    def test_env_var_override(self):
        """Test environment variable override"""
        with patch.dict(os.environ, {'PORT': '9000'}):
            config = ConfigManager()
            assert config.get('app.port') == 9000
    
    def test_database_url_override(self):
        """Test database URL override"""
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            config = ConfigManager()
            assert config.get_database_url() == 'postgresql://test:test@localhost/test'
    
    def test_gemini_config(self):
        """Test Gemini configuration"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            config = ConfigManager()
            gemini_config = config.get_gemini_config()
            assert gemini_config['api_key'] == 'test-key'
    
    def test_safe_config_masking(self):
        """Test sensitive value masking"""
        config = ConfigManager()
        safe_config = config.get_safe_config()
        
        # Should not contain actual sensitive values
        assert 'api_key' not in str(safe_config) or 'masked' in str(safe_config)
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_environment_checks(self):
        """Test environment checking methods"""
        dev_config = ConfigManager('development')
        prod_config = ConfigManager('production')
        
        assert dev_config.is_development()
        assert not dev_config.is_production()
        assert not prod_config.is_development()
        assert prod_config.is_production()

@pytest.fixture
def mock_config():
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
        return ConfigManager('testing')

def test_configuration_validation(mock_config):
    """Test configuration validation"""
    assert mock_config.get('app.name') is not None
    assert mock_config.get('database.url') is not None
