from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from .manager import config
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        self.setup_database()
    
    def setup_database(self):
        """Setup database engine and session factory"""
        db_url = config.get_database_url()
        
        if not db_url:
            raise ValueError("Database URL not configured")
        
        # Engine configuration based on environment
        engine_config = {
            'echo': config.get('database.echo', False),
            'pool_size': config.get('database.pool_size', 5),
            'pool_timeout': config.get('database.pool_timeout', 30),
            'pool_recycle': config.get('database.pool_recycle', 3600)
        }
        
        # SQLite specific configuration
        if db_url.startswith('sqlite'):
            engine_config.update({
                'poolclass': StaticPool,
                'connect_args': {'check_same_thread': False}
            })
            # Remove pool settings not applicable to SQLite
            engine_config.pop('pool_size')
            engine_config.pop('pool_timeout')
            engine_config.pop('pool_recycle')
        
        # PostgreSQL specific configuration
        elif db_url.startswith('postgresql'):
            if config.get('database.pool_pre_ping'):
                engine_config['pool_pre_ping'] = True
        
        self.engine = create_engine(db_url, **engine_config)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database configured: {db_url.split('://')[0]}://***")
    
    def create_tables(self):
        """Create all database tables"""
        self.Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
    
    def get_session(self):
        """Get database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.engine.connect() as connection:
                from sqlalchemy import text
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database instance
db = DatabaseConfig()
