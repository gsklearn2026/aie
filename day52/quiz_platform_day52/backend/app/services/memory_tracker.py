from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading

class MemoryTracker:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.request_history = deque(maxlen=1000)
            self.endpoint_stats = defaultdict(lambda: {
                'count': 0,
                'total_memory': 0.0,
                'max_memory': 0.0,
                'total_duration': 0.0
            })
            self.memory_timeline = deque(maxlen=720)  # 1 hour at 5s intervals
            self.leak_suspects = defaultdict(int)
            self.initialized = True
    
    def record_request(self, endpoint: str, memory_before: float, 
                      memory_after: float, memory_diff: float, 
                      duration: float, top_allocations: List):
        record = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'memory_before': memory_before,
            'memory_after': memory_after,
            'memory_diff': memory_diff,
            'duration': duration,
            'top_allocations': top_allocations
        }
        
        self.request_history.append(record)
        
        # Update endpoint stats
        stats = self.endpoint_stats[endpoint]
        stats['count'] += 1
        stats['total_memory'] += abs(memory_diff)
        stats['max_memory'] = max(stats['max_memory'], memory_after)
        stats['total_duration'] += duration
        
        # Detect potential leaks
        if memory_diff > 1.0:  # More than 1MB growth
            self.leak_suspects[endpoint] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            'total_requests': len(self.request_history),
            'endpoint_stats': dict(self.endpoint_stats),
            'recent_requests': list(self.request_history)[-10:],
            'leak_suspects': dict(self.leak_suspects),
            'memory_timeline': list(self.memory_timeline)
        }
