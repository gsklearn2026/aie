import time
import os
from datetime import datetime
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import logging

logger = logging.getLogger(__name__)

class BackupMetrics:
    def __init__(self):
        # Backup success/failure counters
        self.backup_success_counter = Counter(
            'backup_success_total', 
            'Total successful backups',
            ['backup_type']
        )
        
        self.backup_failure_counter = Counter(
            'backup_failure_total',
            'Total failed backups', 
            ['backup_type']
        )
        
        # Backup duration histogram
        self.backup_duration = Histogram(
            'backup_duration_seconds',
            'Backup execution time',
            ['backup_type']
        )
        
        # Backup size gauge
        self.backup_size = Gauge(
            'backup_size_bytes',
            'Size of backup files',
            ['backup_type']
        )
        
        # System health gauge
        self.system_health = Gauge(
            'backup_system_health',
            'Overall backup system health (0-1)'
        )
        
        # Start Prometheus metrics server
        try:
            prometheus_port = int(os.environ.get('PROMETHEUS_PORT', 8001))
            start_http_server(prometheus_port)
            logger.info(f"Metrics server started on port {prometheus_port}")
        except Exception as e:
            logger.warning(f"Failed to start metrics server: {e}")
    
    def record_backup_success(self, backup_type: str, size: int):
        """Record successful backup"""
        self.backup_success_counter.labels(backup_type=backup_type).inc()
        self.backup_size.labels(backup_type=backup_type).set(size)
        logger.info(f"Recorded successful {backup_type} backup: {size} bytes")
    
    def record_backup_failure(self, backup_type: str, error: str):
        """Record failed backup"""
        self.backup_failure_counter.labels(backup_type=backup_type).inc()
        logger.error(f"Recorded failed {backup_type} backup: {error}")
    
    def record_backup_duration(self, backup_type: str, duration: float):
        """Record backup execution time"""
        self.backup_duration.labels(backup_type=backup_type).observe(duration)
    
    def record_health_status(self, health_status):
        """Record system health status"""
        health_score = 1.0 if health_status.healthy else 0.5
        self.system_health.set(health_score)

class RecoveryMetrics:
    def __init__(self):
        self.recovery_success_counter = Counter(
            'recovery_success_total',
            'Total successful recoveries',
            ['recovery_type']
        )
        
        self.recovery_failure_counter = Counter(
            'recovery_failure_total', 
            'Total failed recoveries',
            ['recovery_type']
        )
        
        self.recovery_duration = Histogram(
            'recovery_duration_seconds',
            'Recovery execution time',
            ['recovery_type']
        )
        
        # System health gauge
        self.system_health = Gauge(
            'recovery_system_health',
            'Overall recovery system health (0-1)'
        )
    
    def record_recovery_success(self, recovery_type: str, duration: float):
        """Record successful recovery"""
        self.recovery_success_counter.labels(recovery_type=recovery_type).inc()
        self.recovery_duration.labels(recovery_type=recovery_type).observe(duration)
    
    def record_recovery_failure(self, recovery_type: str):
        """Record failed recovery"""
        self.recovery_failure_counter.labels(recovery_type=recovery_type).inc()
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics for API response"""
        return {
            "backup_success_rate": self._calculate_success_rate(),
            "average_backup_duration": self._get_average_duration(),
            "system_health_score": self._get_system_health_score(),
            "total_backups_today": self._get_daily_backup_count(),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate backup success rate"""
        # This would calculate from actual metrics in production
        return 0.95  # 95% success rate for demo
    
    def _get_average_duration(self) -> float:
        """Get average backup duration"""
        return 847.3  # Demo value
    
    def _get_daily_backup_count(self) -> int:
        """Get number of backups executed today"""
        return 24  # Demo value
    
    def _get_system_health_score(self) -> float:
        """Get system health score"""
        # For demo purposes, return a healthy score
        # In production, this would calculate from actual metrics
        return 0.98  # 98% health score
