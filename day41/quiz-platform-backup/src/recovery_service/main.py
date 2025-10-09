from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from .recovery_orchestrator import RecoveryOrchestrator
# from .recovery_strategies import PointInTimeRecovery, FullRecovery  # TODO: Implement recovery strategies
from ..monitoring.metrics import RecoveryMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quiz Platform Recovery Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
recovery_orchestrator = RecoveryOrchestrator()
recovery_metrics = RecoveryMetrics()

class RecoveryRequest(BaseModel):
    recovery_type: str  # 'point_in_time' or 'full'
    target_time: Optional[datetime] = None
    backup_file: Optional[str] = None
    dry_run: bool = False

class RecoveryStatus(BaseModel):
    recovery_id: str
    status: str
    progress: float
    message: str
    started_at: datetime
    estimated_completion: Optional[datetime] = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/backups")
async def list_available_backups():
    """List all available backups for recovery"""
    try:
        backups = await recovery_orchestrator.list_available_backups()
        return {"backups": backups}
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recovery/start")
async def start_recovery(request: RecoveryRequest, background_tasks: BackgroundTasks):
    """Start a database recovery operation"""
    try:
        recovery_id = await recovery_orchestrator.start_recovery(
            recovery_type=request.recovery_type,
            target_time=request.target_time,
            backup_file=request.backup_file,
            dry_run=request.dry_run
        )
        
        # Start recovery in background
        background_tasks.add_task(
            recovery_orchestrator.execute_recovery, 
            recovery_id
        )
        
        return {"recovery_id": recovery_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start recovery: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recovery/{recovery_id}/status")
async def get_recovery_status(recovery_id: str):
    """Get the status of a recovery operation"""
    try:
        status = await recovery_orchestrator.get_recovery_status(recovery_id)
        if not status:
            raise HTTPException(status_code=404, detail="Recovery not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recovery status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recovery/history")
async def get_recovery_history(limit: int = 50):
    """Get recovery operation history"""
    try:
        history = await recovery_orchestrator.get_recovery_history(limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Failed to get recovery history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recovery/{recovery_id}/cancel")
async def cancel_recovery(recovery_id: str):
    """Cancel a running recovery operation"""
    try:
        result = await recovery_orchestrator.cancel_recovery(recovery_id)
        return {"cancelled": result}
    except Exception as e:
        logger.error(f"Failed to cancel recovery: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get recovery and backup metrics"""
    try:
        metrics = await recovery_metrics.get_all_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
