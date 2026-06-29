import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models.dossier import Dossier, DossierStatus
from app.models.entity import LegalEntity
from app.schemas.dossier import (
    DossierCreate,
    DossierListResponse,
    DossierResponse,
    DossierStatusUpdate,
)
from app.services.audit_service import log_action

router = APIRouter(prefix="/dossiers", tags=["dossiers"])

VALID_TRANSITIONS: dict[str, set[str]] = {
    DossierStatus.DRAFT.value: {DossierStatus.IN_REVIEW.value},
    DossierStatus.IN_REVIEW.value: {
        DossierStatus.APPROVED.value,
        DossierStatus.REJECTED.value,
        DossierStatus.NEEDS_UPDATE.value,
    },
    DossierStatus.SAFE.value: {
        DossierStatus.APPROVED.value,
        DossierStatus.NEEDS_UPDATE.value,
    },
    DossierStatus.REVIEW_REQUIRED.value: {
        DossierStatus.APPROVED.value,
        DossierStatus.REJECTED.value,
        DossierStatus.NEEDS_UPDATE.value,
    },
    DossierStatus.HIGH_RISK.value: {
        DossierStatus.REJECTED.value,
        DossierStatus.NEEDS_UPDATE.value,
    },
    DossierStatus.NEEDS_UPDATE.value: {DossierStatus.IN_REVIEW.value},
    DossierStatus.APPROVED.value: {DossierStatus.NEEDS_UPDATE.value},
    DossierStatus.REJECTED.value: {
        DossierStatus.IN_REVIEW.value,
        DossierStatus.NEEDS_UPDATE.value,
    },
}


@router.post("", response_model=DossierResponse, status_code=201)
async def create_dossier(payload: DossierCreate, db: AsyncSession = Depends(get_db)):
    entity = await db.get(LegalEntity, payload.entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    dossier = Dossier(entity_id=payload.entity_id, notes=payload.notes)
    db.add(dossier)
    await db.flush()

    await log_action(
        db,
        action="dossier.created",
        dossier_id=dossier.id,
        entity_id=payload.entity_id,
        details={"rfc": entity.rfc},
    )
    await db.commit()
    return await _get_dossier_or_404(db, dossier.id)


@router.get("", response_model=list[DossierListResponse])
async def list_dossiers(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Dossier)
        .join(LegalEntity)
        .options(selectinload(Dossier.entity))
        .offset(skip)
        .limit(limit)
        .order_by(Dossier.created_at.desc())
    )
    if status:
        query = query.where(Dossier.status == status)
    if search:
        query = query.where(
            LegalEntity.rfc.icontains(search)
            | LegalEntity.razon_social.icontains(search)
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats")
async def dossier_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Dossier.status, func.count(Dossier.id)).group_by(Dossier.status)
    )
    return {row[0]: row[1] for row in result.all()}


@router.get("/{dossier_id}", response_model=DossierResponse)
async def get_dossier(dossier_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _get_dossier_or_404(db, dossier_id)


@router.patch("/{dossier_id}/status", response_model=DossierResponse)
async def update_dossier_status(
    dossier_id: uuid.UUID,
    payload: DossierStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    dossier = await _get_dossier_or_404(db, dossier_id)
    allowed = VALID_TRANSITIONS.get(dossier.status, set())

    if payload.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{dossier.status}' to '{payload.status}'",
        )

    if payload.status == DossierStatus.APPROVED.value:
        if dossier.current_risk_classification == DossierStatus.HIGH_RISK.value:
            raise HTTPException(
                status_code=400, detail="Cannot approve a high-risk dossier"
            )

    old_status = dossier.status
    dossier.status = payload.status

    if payload.status == DossierStatus.APPROVED.value:
        dossier.approved_by = payload.approved_by
        dossier.approved_at = datetime.now(timezone.utc)

    if payload.notes:
        dossier.notes = payload.notes

    await log_action(
        db,
        action="dossier.status_changed",
        dossier_id=dossier.id,
        entity_id=dossier.entity_id,
        details={"from": old_status, "to": payload.status},
    )
    await db.commit()
    return await _get_dossier_or_404(db, dossier_id)


@router.delete("/{dossier_id}", status_code=204)
async def delete_dossier(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    dossier = await _get_dossier_or_404(db, dossier_id)
    entity_id = dossier.entity_id

    await log_action(
        db,
        action="dossier.deleted",
        dossier_id=dossier.id,
        entity_id=entity_id,
    )
    await db.delete(dossier)
    await db.flush()

    other = await db.execute(
        select(func.count(Dossier.id)).where(
            Dossier.entity_id == entity_id, Dossier.id != dossier_id
        )
    )
    if other.scalar() == 0:
        entity = await db.get(LegalEntity, entity_id)
        if entity:
            await db.delete(entity)

    await db.commit()


async def _get_dossier_or_404(db: AsyncSession, dossier_id: uuid.UUID) -> Dossier:
    result = await db.execute(
        select(Dossier)
        .where(Dossier.id == dossier_id)
        .options(
            selectinload(Dossier.entity).selectinload(LegalEntity.representatives),
            selectinload(Dossier.entity).selectinload(LegalEntity.shareholders),
        )
    )
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return dossier
