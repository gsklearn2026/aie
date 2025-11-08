from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import weakref
import os

class CacheManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.cache = weakref.WeakValueDictionary()
            self.cache_metadata = {}
            self.sessions = {}
            self.cache_ttl = int(os.getenv('CACHE_TTL_SECONDS', 3600))
            self.session_ttl = int(os.getenv('SESSION_TTL_SECONDS', 1800))
            self.initialized = True
    
    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cache with TTL"""
        ttl = ttl or self.cache_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        # Store strong reference in metadata, weak ref in cache
        self.cache_metadata[key] = {
            'value': value,
            'expiry': expiry,
            'created': datetime.now()
        }
        
        try:
            self.cache[key] = value
        except TypeError:
            # If value can't be weakly referenced, store in metadata only
            pass
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache if not expired"""
        if key in self.cache_metadata:
            metadata = self.cache_metadata[key]
            if datetime.now() < metadata['expiry']:
                return metadata['value']
            else:
                del self.cache_metadata[key]
        return None
    
    async def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, meta in self.cache_metadata.items()
            if now >= meta['expiry']
        ]
        
        for key in expired_keys:
            del self.cache_metadata[key]
            if key in self.cache:
                del self.cache[key]
        
        return len(expired_keys)
    
    async def cleanup_sessions(self) -> int:
        """Remove expired sessions"""
        now = datetime.now()
        expired_sessions = [
            sid for sid, data in self.sessions.items()
            if now >= data.get('expiry', now)
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
        
        return len(expired_sessions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache_metadata),
            'session_count': len(self.sessions),
            'cache_memory_kb': sum(
                len(str(v)) for v in self.cache_metadata.values()
            ) / 1024
        }
