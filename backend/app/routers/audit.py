import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse

router = APIRouter(tags=["audit"])


@router.get("/audit-log", response_model=list[AuditLogResponse])
async def global_audit_log(
    skip: int = 0,
    limit: int = 100,
    action: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog).offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
    if action:
        query = query.where(AuditLog.action == action)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/dossiers/{dossier_id}/audit-log", response_model=list[AuditLogResponse])
async def dossier_audit_log(
    dossier_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(AuditLog)
        .where(AuditLog.dossier_id == dossier_id)
        .offset(skip)
        .limit(limit)
        .order_by(AuditLog.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()
