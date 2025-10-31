import pytest
from unittest.mock import patch, MagicMock
from src.config.database import DatabaseConfig

class TestDatabaseConfig:
    
    @patch('src.config.database.create_engine')
    def test_sqlite_configuration(self, mock_create_engine):
        """Test SQLite database configuration"""
        with patch('src.config.database.config') as mock_config:
            mock_config.get_database_url.return_value = 'sqlite:///test.db'
            mock_config.get.side_effect = lambda key, default=None: {
                'database.echo': True,
                'database.pool_size': 1
            }.get(key, default)
            
            db_config = DatabaseConfig()
            
            mock_create_engine.assert_called_once()
            args, kwargs = mock_create_engine.call_args
            assert args[0] == 'sqlite:///test.db'
            assert 'poolclass' in kwargs
    
    @patch('src.config.database.create_engine')
    def test_postgresql_configuration(self, mock_create_engine):
        """Test PostgreSQL database configuration"""
        with patch('src.config.database.config') as mock_config:
            mock_config.get_database_url.return_value = 'postgresql://user:pass@localhost/db'
            mock_config.get.side_effect = lambda key, default=None: {
                'database.echo': False,
                'database.pool_size': 10,
                'database.pool_pre_ping': True
            }.get(key, default)
            
            db_config = DatabaseConfig()
            
            mock_create_engine.assert_called_once()
            args, kwargs = mock_create_engine.call_args
            assert args[0] == 'postgresql://user:pass@localhost/db'
            assert kwargs['pool_pre_ping'] == True
    
    def test_health_check_success(self):
        """Test successful health check"""
        with patch('src.config.database.config'), \
             patch('src.config.database.create_engine') as mock_engine:
            
            mock_connection = MagicMock()
            mock_engine.return_value.connect.return_value.__enter__.return_value = mock_connection
            
            db_config = DatabaseConfig()
            assert db_config.health_check() == True
            mock_connection.execute.assert_called_once_with("SELECT 1")
