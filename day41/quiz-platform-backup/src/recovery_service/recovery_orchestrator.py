import asyncio
import uuid
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class RecoveryStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"  
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class RecoveryOperation:
    recovery_id: str
    recovery_type: str
    status: RecoveryStatus
    progress: float
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    target_time: Optional[datetime] = None
    backup_file: Optional[str] = None
    dry_run: bool = False
    error: Optional[str] = None

class RecoveryOrchestrator:
    def __init__(self):
        self.active_recoveries: Dict[str, RecoveryOperation] = {}
        self.recovery_history: List[RecoveryOperation] = []
        self.backup_dir = os.environ.get('BACKUP_STORAGE_PATH', './backups')
    
    async def start_recovery(self, recovery_type: str, target_time: Optional[datetime] = None,
                           backup_file: Optional[str] = None, dry_run: bool = False) -> str:
        """Start a new recovery operation"""
        recovery_id = str(uuid.uuid4())[:8]
        
        operation = RecoveryOperation(
            recovery_id=recovery_id,
            recovery_type=recovery_type,
            status=RecoveryStatus.PENDING,
            progress=0.0,
            message="Recovery queued for execution",
            started_at=datetime.utcnow(),
            target_time=target_time,
            backup_file=backup_file,
            dry_run=dry_run
        )
        
        self.active_recoveries[recovery_id] = operation
        logger.info(f"Started recovery operation {recovery_id}")
        
        return recovery_id
    
    async def execute_recovery(self, recovery_id: str):
        """Execute the recovery operation"""
        if recovery_id not in self.active_recoveries:
            logger.error(f"Recovery {recovery_id} not found")
            return
        
        operation = self.active_recoveries[recovery_id]
        
        try:
            operation.status = RecoveryStatus.RUNNING
            operation.message = "Recovery in progress..."
            
            if operation.recovery_type == "point_in_time":
                await self._execute_point_in_time_recovery(operation)
            elif operation.recovery_type == "full":
                await self._execute_full_recovery(operation)
            else:
                raise ValueError(f"Unknown recovery type: {operation.recovery_type}")
            
            operation.status = RecoveryStatus.COMPLETED
            operation.progress = 100.0
            operation.message = "Recovery completed successfully"
            operation.completed_at = datetime.utcnow()
            
        except Exception as e:
            operation.status = RecoveryStatus.FAILED
            operation.error = str(e)
            operation.message = f"Recovery failed: {str(e)}"
            logger.error(f"Recovery {recovery_id} failed: {e}")
        
        finally:
            # Move to history
            self.recovery_history.append(operation)
            if recovery_id in self.active_recoveries:
                del self.active_recoveries[recovery_id]
    
    async def _execute_point_in_time_recovery(self, operation: RecoveryOperation):
        """Execute point-in-time recovery"""
        logger.info(f"Executing PITR for {operation.recovery_id}")
        
        # Phase 1: Find appropriate backup
        operation.progress = 10.0
        operation.message = "Locating backup files..."
        await asyncio.sleep(2)  # Simulate work
        
        backup_file = await self._find_backup_for_time(operation.target_time)
        if not backup_file:
            raise Exception("No suitable backup found for target time")
        
        # Phase 2: Restore base backup
        operation.progress = 30.0
        operation.message = "Restoring base backup..."
        await asyncio.sleep(5)  # Simulate restore
        
        # Phase 3: Apply WAL logs
        operation.progress = 60.0
        operation.message = "Applying transaction logs..."
        await asyncio.sleep(8)  # Simulate WAL replay
        
        # Phase 4: Verify recovery
        operation.progress = 90.0
        operation.message = "Verifying restored data..."
        await asyncio.sleep(3)  # Simulate verification
    
    async def _execute_full_recovery(self, operation: RecoveryOperation):
        """Execute full database recovery"""
        logger.info(f"Executing full recovery for {operation.recovery_id}")
        
        # Phase 1: Prepare for recovery
        operation.progress = 15.0
        operation.message = "Preparing recovery environment..."
        await asyncio.sleep(3)
        
        # Phase 2: Restore from backup
        operation.progress = 50.0 
        operation.message = "Restoring database from backup..."
        await asyncio.sleep(10)  # Simulate full restore
        
        # Phase 3: Rebuild indexes
        operation.progress = 80.0
        operation.message = "Rebuilding database indexes..."
        await asyncio.sleep(5)
        
        # Phase 4: Final verification
        operation.progress = 95.0
        operation.message = "Running final verification..."
        await asyncio.sleep(2)
    
    async def _find_backup_for_time(self, target_time: datetime) -> Optional[str]:
        """Find the best backup file for the target time"""
        if not target_time:
            # Return most recent backup
            return await self._get_most_recent_backup()
        
        # Find backup closest to but before target time
        best_backup = None
        best_time_diff = None
        
        for backup_type in ['warm', 'cold']:  # PITR usually uses warm/cold
            backup_path = os.path.join(self.backup_dir, backup_type)
            if os.path.exists(backup_path):
                for filename in os.listdir(backup_path):
                    file_path = os.path.join(backup_path, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time <= target_time:
                        time_diff = (target_time - file_time).total_seconds()
                        if best_time_diff is None or time_diff < best_time_diff:
                            best_backup = file_path
                            best_time_diff = time_diff
        
        return best_backup
    
    async def _get_most_recent_backup(self) -> Optional[str]:
        """Get the most recent backup file"""
        most_recent = None
        most_recent_time = None
        
        for backup_type in ['hot', 'warm', 'cold']:
            backup_path = os.path.join(self.backup_dir, backup_type)
            if os.path.exists(backup_path):
                for filename in os.listdir(backup_path):
                    file_path = os.path.join(backup_path, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if most_recent_time is None or file_time > most_recent_time:
                        most_recent = file_path
                        most_recent_time = file_time
        
        return most_recent
    
    async def get_recovery_status(self, recovery_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a recovery operation"""
        # Check active recoveries
        if recovery_id in self.active_recoveries:
            return asdict(self.active_recoveries[recovery_id])
        
        # Check history
        for operation in self.recovery_history:
            if operation.recovery_id == recovery_id:
                return asdict(operation)
        
        return None
    
    async def list_available_backups(self) -> List[Dict[str, Any]]:
        """List all available backup files"""
        backups = []
        
        for backup_type in ['hot', 'warm', 'cold']:
            backup_path = os.path.join(self.backup_dir, backup_type)
            if os.path.exists(backup_path):
                for filename in os.listdir(backup_path):
                    file_path = os.path.join(backup_path, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        backups.append({
                            'filename': filename,
                            'type': backup_type,
                            'size': stat.st_size,
                            'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'file_path': file_path
                        })
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    async def get_recovery_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recovery operation history"""
        history = sorted(self.recovery_history, key=lambda x: x.started_at, reverse=True)
        return [asdict(op) for op in history[:limit]]
    
    async def cancel_recovery(self, recovery_id: str) -> bool:
        """Cancel a running recovery operation"""
        if recovery_id in self.active_recoveries:
            operation = self.active_recoveries[recovery_id]
            if operation.status == RecoveryStatus.RUNNING:
                operation.status = RecoveryStatus.CANCELLED
                operation.message = "Recovery cancelled by user"
                operation.completed_at = datetime.utcnow()
                
                # Move to history
                self.recovery_history.append(operation)
                del self.active_recoveries[recovery_id]
                
                logger.info(f"Recovery {recovery_id} cancelled")
                return True
        
        return False
