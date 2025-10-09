import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SystemHealthStatus:
    healthy: bool
    issues: List[str]
    last_successful_backup: datetime
    disk_usage_percent: float
    replication_lag_seconds: float

class BackupOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backup_dir = os.environ.get('BACKUP_STORAGE_PATH', './backups')
    
    async def check_system_health(self) -> SystemHealthStatus:
        """Check overall backup system health"""
        issues = []
        
        # Check disk space
        disk_usage = await self._check_disk_usage()
        if disk_usage > 85:
            issues.append(f"Disk usage at {disk_usage}%")
        
        # Check replication lag
        replication_lag = await self._check_replication_lag()
        if replication_lag > 300:  # 5 minutes
            issues.append(f"Replication lag: {replication_lag}s")
        
        # Check last successful backup
        last_backup = await self._get_last_successful_backup()
        if not last_backup or (datetime.utcnow() - last_backup).seconds > 7200:  # 2 hours
            issues.append("No recent successful backup")
        
        return SystemHealthStatus(
            healthy=len(issues) == 0,
            issues=issues,
            last_successful_backup=last_backup,
            disk_usage_percent=disk_usage,
            replication_lag_seconds=replication_lag
        )
    
    async def cleanup_old_backups(self, backup_type: str, cutoff_date: datetime) -> int:
        """Clean up old backup files"""
        cleaned_count = 0
        backup_path = os.path.join(self.backup_dir, backup_type)
        
        if not os.path.exists(backup_path):
            return 0
        
        for filename in os.listdir(backup_path):
            file_path = os.path.join(backup_path, filename)
            
            # Check file modification time
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_mtime < cutoff_date:
                try:
                    if os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                    cleaned_count += 1
                    self.logger.info(f"Cleaned up old backup: {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to clean up {filename}: {e}")
        
        return cleaned_count
    
    async def _check_disk_usage(self) -> float:
        """Check disk usage percentage"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.backup_dir)
            return (used / total) * 100
        except Exception:
            return 0.0
    
    async def _check_replication_lag(self) -> float:
        """Check database replication lag in seconds"""
        # In production, query actual replication lag
        # For demo, return simulated value
        return 30.0
    
    async def _get_last_successful_backup(self) -> datetime:
        """Get timestamp of last successful backup"""
        latest_time = None
        
        for backup_type in ['hot', 'warm', 'cold']:
            backup_path = os.path.join(self.backup_dir, backup_type)
            if os.path.exists(backup_path):
                for filename in os.listdir(backup_path):
                    file_path = os.path.join(backup_path, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if not latest_time or file_mtime > latest_time:
                        latest_time = file_mtime
        
        return latest_time
