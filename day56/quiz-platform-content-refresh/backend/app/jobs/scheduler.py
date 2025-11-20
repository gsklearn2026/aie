from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import structlog

from app.core.config import settings
from app.jobs.refresh_jobs import freshness_scan_job, stale_content_job

logger = structlog.get_logger()

scheduler = None

def start_scheduler():
    global scheduler
    
    jobstores = {
        'default': SQLAlchemyJobStore(url=settings.DATABASE_URL_SYNC)
    }
    
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults
    )
    
    # Add jobs
    scheduler.add_job(
        freshness_scan_job,
        'interval',
        hours=settings.FRESHNESS_SCAN_HOURS,
        id='freshness_scan',
        replace_existing=True
    )
    
    scheduler.add_job(
        stale_content_job,
        'cron',
        hour=settings.STALE_PROCESS_HOUR,
        id='stale_content_process',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started", jobs=len(scheduler.get_jobs()))

def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")

def get_scheduler():
    return scheduler
