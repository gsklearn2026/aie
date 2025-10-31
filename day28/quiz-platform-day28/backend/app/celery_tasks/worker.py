from celery import Celery
from sqlalchemy.orm import Session
import os

from ..config.database import SessionLocal
from ..services.export_service import ExportService

# Celery configuration
celery_app = Celery(
    "export_worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def process_export_job(job_id: str):
    """Celery task to process export job"""
    db = SessionLocal()
    try:
        export_service = ExportService(db)
        # Run async function in sync context
        import asyncio
        asyncio.run(export_service.process_export_job(job_id))
    finally:
        db.close()
