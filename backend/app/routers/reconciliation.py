import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models.dossier import Dossier
from app.models.entity import LegalEntity
from app.schemas.reconciliation import ReconciliationResultResponse, ReconciliationSummary
from app.services.document_service import list_documents
from app.services.reconciliation_service import get_reconciliation_results, run_reconciliation

router = APIRouter(tags=["reconciliation"])


@router.post("/dossiers/{dossier_id}/reconciliation", response_model=ReconciliationSummary)
async def run_dossier_reconciliation(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    from sqlalchemy import select
    result = await db.execute(
        select(LegalEntity)
        .where(LegalEntity.id == dossier.entity_id)
        .options(selectinload(LegalEntity.representatives))
    )
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    documents = await list_documents(db, dossier_id)

    results = await run_reconciliation(
        db, dossier_id=dossier_id, entity=entity, documents=documents
    )
    await db.commit()

    for r in results:
        await db.refresh(r)

    matches = sum(1 for r in results if r.match)
    discrepancies = len(results) - matches
    has_critical = any(r.severity == "critical" for r in results)

    return ReconciliationSummary(
        total_comparisons=len(results),
        matches=matches,
        discrepancies=discrepancies,
        has_critical=has_critical,
        results=results,
    )


@router.get("/dossiers/{dossier_id}/reconciliation", response_model=list[ReconciliationResultResponse])
async def get_dossier_reconciliation(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_reconciliation_results(db, dossier_id)
