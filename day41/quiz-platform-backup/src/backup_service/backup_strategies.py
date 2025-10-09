import asyncio
import subprocess
import gzip
import os
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class BackupResult:
    success: bool
    backup_type: str
    file_path: Optional[str] = None
    size: Optional[int] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None

class BackupStrategy(ABC):
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.backup_dir = os.environ.get('BACKUP_STORAGE_PATH', './backups')
    
    @abstractmethod
    async def execute(self) -> BackupResult:
        pass

class HotBackup(BackupStrategy):
    """Continuous WAL-based backup for zero data loss"""
    
    async def execute(self) -> BackupResult:
        start_time = datetime.utcnow()
        
        try:
            # WAL streaming backup simulation
            backup_path = f"{self.backup_dir}/hot/wal_{start_time.strftime('%Y%m%d_%H%M%S')}.backup"
            
            # Create backup directory
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Simulate WAL backup (in production, use pg_receivewal)
            cmd = [
                'pg_dump',
                '--format=custom',
                '--no-owner',
                '--no-privileges',
                '--compress=9',
                '--file', backup_path,
                os.environ.get('DATABASE_URL', '').replace('postgresql://', 'postgres://')
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                file_size = os.path.getsize(backup_path)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                return BackupResult(
                    success=True,
                    backup_type="hot",
                    file_path=backup_path,
                    size=file_size,
                    duration=duration,
                    timestamp=start_time
                )
            else:
                return BackupResult(
                    success=False,
                    backup_type="hot",
                    error=stderr.decode() if stderr else "Unknown error",
                    timestamp=start_time
                )
                
        except Exception as e:
            return BackupResult(
                success=False,
                backup_type="hot",
                error=str(e),
                timestamp=start_time
            )

class WarmBackup(BackupStrategy):
    """Point-in-time backup with transaction logs"""
    
    async def execute(self) -> BackupResult:
        start_time = datetime.utcnow()
        
        try:
            backup_path = f"{self.backup_dir}/warm/pitr_{start_time.strftime('%Y%m%d_%H%M%S')}.backup"
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Point-in-time backup with pg_basebackup simulation
            cmd = [
                'pg_dump',
                '--format=directory',
                '--no-owner',
                '--no-privileges',
                '--compress=5',
                '--file', backup_path,
                os.environ.get('DATABASE_URL', '').replace('postgresql://', 'postgres://')
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Calculate directory size
                file_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(backup_path)
                    for filename in filenames
                )
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                return BackupResult(
                    success=True,
                    backup_type="warm",
                    file_path=backup_path,
                    size=file_size,
                    duration=duration,
                    timestamp=start_time
                )
            else:
                return BackupResult(
                    success=False,
                    backup_type="warm",
                    error=stderr.decode() if stderr else "Unknown error",
                    timestamp=start_time
                )
                
        except Exception as e:
            return BackupResult(
                success=False,
                backup_type="warm",
                error=str(e),
                timestamp=start_time
            )

class ColdBackup(BackupStrategy):
    """Full database dump for disaster recovery"""
    
    async def execute(self) -> BackupResult:
        start_time = datetime.utcnow()
        
        try:
            backup_path = f"{self.backup_dir}/cold/full_{start_time.strftime('%Y%m%d_%H%M%S')}.sql.gz"
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Full database dump
            cmd = [
                'pg_dump',
                '--format=plain',
                '--no-owner',
                '--no-privileges',
                '--clean',
                '--if-exists',
                os.environ.get('DATABASE_URL', '').replace('postgresql://', 'postgres://')
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Compress the output
                with gzip.open(backup_path, 'wt') as f:
                    f.write(stdout.decode())
                
                file_size = os.path.getsize(backup_path)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                return BackupResult(
                    success=True,
                    backup_type="cold",
                    file_path=backup_path,
                    size=file_size,
                    duration=duration,
                    timestamp=start_time
                )
            else:
                return BackupResult(
                    success=False,
                    backup_type="cold",
                    error=stderr.decode() if stderr else "Unknown error",
                    timestamp=start_time
                )
                
        except Exception as e:
            return BackupResult(
                success=False,
                backup_type="cold",
                error=str(e),
                timestamp=start_time
            )
