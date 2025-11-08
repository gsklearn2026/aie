import asyncio
from datetime import datetime, timedelta
from app.services.cache_manager import CacheManager

class CleanupScheduler:
    def __init__(self):
        self.cache_manager = CacheManager()
        self.running = False
        self.task = None
        self.cleanup_interval = 300  # 5 minutes
    
    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
    
    async def _cleanup_loop(self):
        while self.running:
            try:
                await self._run_cleanup()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cleanup error: {e}")
                await asyncio.sleep(self.cleanup_interval)
    
    async def _run_cleanup(self):
        print(f"🧹 Running cleanup at {datetime.now()}")
        
        # Clean expired cache entries
        expired_count = await self.cache_manager.cleanup_expired()
        
        # Clean expired sessions
        session_count = await self.cache_manager.cleanup_sessions()
        
        print(f"   Cleaned {expired_count} cache entries, {session_count} sessions")
