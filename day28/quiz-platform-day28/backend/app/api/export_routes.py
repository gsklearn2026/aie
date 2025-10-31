from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import mimetypes

from ..config.database import get_db
from ..services.export_service import ExportService
from ..models.export_models import ExportRequest, ExportJobResponse, ExportProgress

router = APIRouter()

@router.post("/create", response_model=dict)
async def create_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "demo_user",  # In real app, get from auth
    db: Session = Depends(get_db)
):
    """Create a new export job"""
    export_service = ExportService(db)
    
    job_id = await export_service.create_export_job(
        request.dict(), user_id
    )
    
    # Process export in background
    background_tasks.add_task(
        export_service.process_export_job, job_id
    )
    
    return {"job_id": job_id, "status": "queued"}

@router.get("/status/{job_id}", response_model=dict)
async def get_export_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get export job status"""
    export_service = ExportService(db)
    status = export_service.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Export job not found")
    
    return status

@router.get("/download/{job_id}")
async def download_export(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Download completed export file"""
    export_service = ExportService(db)
    status = export_service.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Export job not found")
    
    if status['status'] != 'completed':
        raise HTTPException(
            status_code=400, 
            detail=f"Export not ready. Status: {status['status']}"
        )
    
    # Get job from database to get file path
    from ..models.export_models import ExportJob
    job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
    
    if not job.file_path or not os.path.exists(job.file_path):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(job.file_path)
    if not content_type:
        content_type = "application/octet-stream"
    
    # Return file
    filename = os.path.basename(job.file_path)
    return FileResponse(
        job.file_path,
        media_type=content_type,
        filename=filename
    )

@router.get("/jobs", response_model=List[dict])
async def list_export_jobs(
    user_id: str = "demo_user",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List export jobs for user"""
    from ..models.export_models import ExportJob
    
    jobs = db.query(ExportJob)\
        .filter(ExportJob.user_id == user_id)\
        .order_by(ExportJob.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [
        {
            'job_id': job.job_id,
            'format': job.export_format.value,
            'status': job.status.value,
            'progress': job.progress,
            'total_records': job.total_records,
            'file_size': job.file_size,
            'created_at': job.created_at,
            'completed_at': job.completed_at
        }
        for job in jobs
    ]
