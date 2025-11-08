from fastapi import APIRouter
from app.services.memory_tracker import MemoryTracker
from app.services.cache_manager import CacheManager
import psutil
import gc

router = APIRouter()
tracker = MemoryTracker()
cache_manager = CacheManager()

@router.get("/stats")
async def get_memory_stats():
    """Get memory statistics"""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        'process': {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        },
        'tracker': tracker.get_statistics(),
        'cache': cache_manager.get_stats(),
        'gc': {
            'collections': gc.get_count(),
            'objects': len(gc.get_objects())
        }
    }

@router.post("/gc")
async def trigger_gc():
    """Manually trigger garbage collection"""
    collected = gc.collect()
    return {'collected': collected, 'status': 'completed'}

@router.post("/cache/clear")
async def clear_cache():
    """Clear all cache"""
    cache_manager.cache_metadata.clear()
    return {'status': 'cache_cleared'}
