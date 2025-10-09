import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from .backup_orchestrator import BackupOrchestrator
from .backup_strategies import HotBackup, WarmBackup, ColdBackup
from .backup_validator import BackupValidator
from ..monitoring.metrics import BackupMetrics
from ..database.connection import DatabaseManager
from ..utils.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self):
        self.settings = Settings()
        self.db_manager = DatabaseManager()
        self.orchestrator = BackupOrchestrator()
        self.validator = BackupValidator()
        self.metrics = BackupMetrics()
        
        # Initialize backup strategies
        self.hot_backup = HotBackup(self.db_manager)
        self.warm_backup = WarmBackup(self.db_manager)
        self.cold_backup = ColdBackup(self.db_manager)
    
    async def start_backup_scheduler(self):
        """Start the backup scheduling system"""
        logger.info("Starting backup scheduler...")
        
        tasks = [
            self._schedule_hot_backups(),
            self._schedule_warm_backups(),
            self._schedule_cold_backups(),
            self._monitor_backup_health()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _schedule_hot_backups(self):
        """Schedule continuous hot backups"""
        while True:
            try:
                logger.info("Executing hot backup...")
                backup_result = await self.hot_backup.execute()
                
                if backup_result.success:
                    validation_result = await self.validator.validate_backup(backup_result)
                    self.metrics.record_backup_success("hot", backup_result.size)
                else:
                    self.metrics.record_backup_failure("hot", backup_result.error)
                    
            except Exception as e:
                logger.error(f"Hot backup failed: {e}")
                self.metrics.record_backup_failure("hot", str(e))
            
            await asyncio.sleep(self.settings.HOT_BACKUP_INTERVAL)
    
    async def _schedule_warm_backups(self):
        """Schedule hourly warm backups"""
        while True:
            try:
                logger.info("Executing warm backup...")
                backup_result = await self.warm_backup.execute()
                
                if backup_result.success:
                    validation_result = await self.validator.validate_backup(backup_result)
                    self.metrics.record_backup_success("warm", backup_result.size)
                else:
                    self.metrics.record_backup_failure("warm", backup_result.error)
                    
            except Exception as e:
                logger.error(f"Warm backup failed: {e}")
                self.metrics.record_backup_failure("warm", str(e))
            
            await asyncio.sleep(self.settings.WARM_BACKUP_INTERVAL)
    
    async def _schedule_cold_backups(self):
        """Schedule daily cold backups"""
        while True:
            try:
                logger.info("Executing cold backup...")
                backup_result = await self.cold_backup.execute()
                
                if backup_result.success:
                    validation_result = await self.validator.validate_backup(backup_result)
                    self.metrics.record_backup_success("cold", backup_result.size)
                    await self._cleanup_old_backups()
                else:
                    self.metrics.record_backup_failure("cold", backup_result.error)
                    
            except Exception as e:
                logger.error(f"Cold backup failed: {e}")
                self.metrics.record_backup_failure("cold", str(e))
            
            await asyncio.sleep(self.settings.COLD_BACKUP_INTERVAL)
    
    async def _monitor_backup_health(self):
        """Monitor overall backup system health"""
        while True:
            try:
                health_status = await self.orchestrator.check_system_health()
                self.metrics.record_health_status(health_status)
                
                if not health_status.healthy:
                    logger.warning(f"Backup system unhealthy: {health_status.issues}")
                    
            except Exception as e:
                logger.error(f"Health monitoring failed: {e}")
            
            await asyncio.sleep(60)  # Check every minute
    
    async def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.settings.BACKUP_RETENTION_DAYS)
        
        for backup_type in ['hot', 'warm', 'cold']:
            cleaned = await self.orchestrator.cleanup_old_backups(backup_type, cutoff_date)
            logger.info(f"Cleaned up {cleaned} old {backup_type} backups")

async def main():
    service = BackupService()
    await service.start_backup_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
