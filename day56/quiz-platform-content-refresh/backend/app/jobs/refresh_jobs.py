import asyncio
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.services.refresh_service import RefreshService

logger = structlog.get_logger()

async def _run_freshness_scan():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        service = RefreshService(session)
        updated = await service.scan_and_update_freshness()
        logger.info("Scheduled freshness scan complete", updated=updated)
    
    await engine.dispose()

async def _run_stale_processing():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        service = RefreshService(session)
        processed = await service.process_pending_jobs(settings.REFRESH_BATCH_SIZE)
        logger.info("Scheduled stale processing complete", processed=processed)
    
    await engine.dispose()

def freshness_scan_job():
    asyncio.run(_run_freshness_scan())

def stale_content_job():
    asyncio.run(_run_stale_processing())
