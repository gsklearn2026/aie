import asyncio
import psutil
import os
from datetime import datetime
from typing import Dict, Any
from collections import deque

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.memory_samples = deque(maxlen=720)  # 1 hour of samples
        self.alert_threshold = float(os.getenv('MEMORY_ALERT_THRESHOLD', 0.85))
        self.memory_limit = float(os.getenv('MEMORY_LIMIT_MB', 4096))
        self.running = False
        self.task = None
    
    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
    
    async def _monitor_loop(self):
        while self.running:
            try:
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = memory_mb / self.memory_limit
                
                sample = {
                    'timestamp': datetime.now().isoformat(),
                    'memory_mb': round(memory_mb, 2),
                    'memory_percent': round(memory_percent * 100, 2),
                    'alert': memory_percent >= self.alert_threshold
                }
                
                self.memory_samples.append(sample)
                
                if sample['alert']:
                    print(f"⚠️  MEMORY ALERT: {memory_mb:.2f}MB ({memory_percent*100:.1f}%)")
                
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(5)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        if not self.memory_samples:
            return {'memory_mb': 0, 'memory_percent': 0, 'alert': False}
        
        current = self.memory_samples[-1]
        history = list(self.memory_samples)
        
        return {
            'current': current,
            'history': history[-60:],  # Last 5 minutes
            'peak': max(s['memory_mb'] for s in history) if history else 0,
            'average': sum(s['memory_mb'] for s in history) / len(history) if history else 0
        }
