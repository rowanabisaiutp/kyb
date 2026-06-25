import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.dossier import Dossier
from app.models.entity import LegalEntity
from app.models.fiscal_check import FiscalListCheck
from app.schemas.fiscal import (
    FiscalCheckResponse,
    FiscalCheckSummary,
    FiscalListsStatus,
)
from app.services.fiscal_service import check_rfc_in_lists, get_lists_status

router = APIRouter(tags=["fiscal"])


@router.post("/dossiers/{dossier_id}/fiscal-check", response_model=FiscalCheckSummary)
async def run_fiscal_check(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    entity = await db.get(LegalEntity, dossier.entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    checks = await check_rfc_in_lists(db, dossier_id=dossier_id, rfc=entity.rfc)
    await db.commit()

    for c in checks:
        await db.refresh(c)

    return FiscalCheckSummary(
        total_lists_checked=len(checks),
        matches_found=sum(1 for c in checks if c.found),
        clean=all(not c.found for c in checks),
        checks=checks,
    )


@router.get(
    "/dossiers/{dossier_id}/fiscal-checks", response_model=list[FiscalCheckResponse]
)
async def list_fiscal_checks(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FiscalListCheck)
        .where(FiscalListCheck.dossier_id == dossier_id)
        .order_by(FiscalListCheck.checked_at.desc())
    )
    return result.scalars().all()


@router.get("/fiscal-lists/status", response_model=FiscalListsStatus)
async def fiscal_lists_status():
    return get_lists_status()
