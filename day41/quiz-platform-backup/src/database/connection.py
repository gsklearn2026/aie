import asyncpg
import psycopg2
from contextlib import asynccontextmanager
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.primary_url = os.environ.get('DATABASE_URL')
        self.backup_url = os.environ.get('BACKUP_DATABASE_URL')
        self._primary_pool = None
        self._backup_pool = None
    
    async def init_pools(self):
        """Initialize database connection pools"""
        self._primary_pool = await asyncpg.create_pool(self.primary_url)
        self._backup_pool = await asyncpg.create_pool(self.backup_url)
        logger.info("Database pools initialized")
    
    @asynccontextmanager
    async def get_primary_connection(self):
        """Get connection to primary database"""
        if not self._primary_pool:
            await self.init_pools()
        
        async with self._primary_pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager  
    async def get_backup_connection(self):
        """Get connection to backup database"""
        if not self._backup_pool:
            await self.init_pools()
            
        async with self._backup_pool.acquire() as connection:
            yield connection
    
    def get_sync_connection(self, url=None):
        """Get synchronous connection for backup operations"""
        connection_url = url or self.primary_url
        return psycopg2.connect(connection_url)
    
    async def close_pools(self):
        """Close all database pools"""
        if self._primary_pool:
            await self._primary_pool.close()
        if self._backup_pool:
            await self._backup_pool.close()
        logger.info("Database pools closed")
