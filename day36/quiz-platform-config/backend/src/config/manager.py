import json
import os
from typing import Any, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Environment-aware configuration management system"""
    
    def __init__(self, env: str = None):
        self.env = env or os.getenv('APP_ENV', 'development')
        self.config: Dict[str, Any] = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load hierarchical configuration: base -> environment -> env vars"""
        try:
            # Load base configuration
            base_config = self._load_config_file('base.json')
            
            # Load environment-specific configuration
            env_config = self._load_config_file(f'{self.env}.json')
            
            # Merge configurations
            self.config = self._deep_merge(base_config, env_config)
            
            # Override with environment variables
            self._apply_env_overrides()
            
            # Validate required settings
            self._validate_config()
            
            logger.info(f"Configuration loaded for environment: {self.env}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load JSON configuration file"""
        config_path = Path(__file__).parent.parent.parent / 'configs' / filename
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {filename}")
            return {}
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            'DATABASE_URL': ['database', 'url'],
            'GEMINI_API_KEY': ['gemini', 'api_key'],
            'SECRET_KEY': ['security', 'secret_key'],
            'PORT': ['app', 'port'],
            'HOST': ['app', 'host'],
            'LOG_LEVEL': ['logging', 'level']
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(self.config, config_path, value)
    
    def _set_nested_value(self, config: Dict, path: list, value: Any):
        """Set nested dictionary value using path"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if path[-1] == 'port':
            value = int(value)
        elif path[-1] in ['debug', 'echo', 'hot_reload']:
            value = value.lower() in ('true', '1', 'yes')
        
        current[path[-1]] = value
    
    def _validate_config(self):
        """Validate required configuration values"""
        required_paths = [
            ['app', 'name'],
            ['app', 'port'],
            ['database', 'url'],
            ['logging', 'level']
        ]
        
        for path in required_paths:
            if not self._get_nested_value(self.config, path):
                raise ValueError(f"Required configuration missing: {'.'.join(path)}")
        
        # Validate Gemini API key in non-development environments
        if self.env != 'development':
            if not self._get_nested_value(self.config, ['gemini', 'api_key']):
                raise ValueError("GEMINI_API_KEY environment variable required")
    
    def _get_nested_value(self, config: Dict, path: list) -> Any:
        """Get nested dictionary value using path"""
        current = config
        for key in path:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = path.split('.')
        return self._get_nested_value(self.config, keys) or default
    
    def get_database_url(self) -> str:
        """Get database URL with environment variable override"""
        return self.get('database.url') or os.getenv('DATABASE_URL')
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini AI configuration"""
        config = self.config.get('gemini', {}).copy()
        config['api_key'] = os.getenv('GEMINI_API_KEY')
        return config
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.env == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.env == 'production'
    
    def get_safe_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive values masked"""
        safe_config = self.config.copy()
        
        # Mask sensitive values
        sensitive_keys = ['api_key', 'secret_key', 'password', 'url']
        return self._mask_sensitive_values(safe_config, sensitive_keys)
    
    def _mask_sensitive_values(self, config: Dict, sensitive_keys: list) -> Dict[str, Any]:
        """Recursively mask sensitive configuration values"""
        if isinstance(config, dict):
            result = {}
            for key, value in config.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    result[key] = '***masked***' if value else None
                elif isinstance(value, dict):
                    result[key] = self._mask_sensitive_values(value, sensitive_keys)
                else:
                    result[key] = value
            return result
        return config

# Global configuration instance
config = ConfigManager()
