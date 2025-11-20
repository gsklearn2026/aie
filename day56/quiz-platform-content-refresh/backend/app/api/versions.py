from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.content import ContentVersion
from app.schemas.content import VersionResponse
from app.services.refresh_service import RefreshService

router = APIRouter()

@router.get("/{content_id}", response_model=List[VersionResponse])
async def get_versions(
    content_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_id == content_id)
        .order_by(ContentVersion.version_number.desc())
    )
    return result.scalars().all()

@router.post("/{content_id}/rollback/{version_number}")
async def rollback_version(
    content_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db)
):
    service = RefreshService(db)
    success = await service.rollback_content(content_id, version_number)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"status": "rolled_back", "version": version_number}
