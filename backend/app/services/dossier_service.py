import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dossier import Dossier, DossierStatus
from app.models.fiscal_check import FiscalListCheck
from app.services.audit_service import log_action
from app.services.document_service import list_documents
from app.services.validity_service import needs_update


async def check_and_update_validity(db: AsyncSession, dossier_id: uuid.UUID) -> str | None:
    dossier = await db.get(Dossier, dossier_id)
    if not dossier or dossier.status in (DossierStatus.DRAFT.value, DossierStatus.REJECTED.value):
        return None

    documents = await list_documents(db, dossier_id)
    fiscal_result = await db.execute(
        select(FiscalListCheck).where(FiscalListCheck.dossier_id == dossier_id)
    )
    fiscal_checks = list(fiscal_result.scalars().all())

    if needs_update(documents, fiscal_checks):
        old_status = dossier.status
        if old_status != DossierStatus.NEEDS_UPDATE.value:
            dossier.status = DossierStatus.NEEDS_UPDATE.value
            await log_action(
                db, action="dossier.auto_needs_update", dossier_id=dossier_id,
                details={"from": old_status, "to": DossierStatus.NEEDS_UPDATE.value},
            )
            await db.flush()
            return DossierStatus.NEEDS_UPDATE.value

    return dossier.status


async def approve_dossier(
    db: AsyncSession, dossier_id: uuid.UUID, approved_by: str
) -> Dossier:
    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise ValueError("Dossier not found")

    if dossier.current_risk_classification == DossierStatus.HIGH_RISK.value:
        raise ValueError("No se puede aprobar un expediente de alto riesgo")

    if dossier.status not in (
        DossierStatus.IN_REVIEW.value,
        DossierStatus.SAFE.value,
        DossierStatus.REVIEW_REQUIRED.value,
    ):
        raise ValueError(f"No se puede aprobar desde el estado '{dossier.status}'")

    old_status = dossier.status
    dossier.status = DossierStatus.APPROVED.value
    dossier.approved_by = approved_by
    dossier.approved_at = datetime.now(timezone.utc)

    await log_action(
        db, action="dossier.approved", dossier_id=dossier_id,
        details={"from": old_status, "approved_by": approved_by},
    )
    await db.flush()
    return dossier


async def reject_dossier(
    db: AsyncSession, dossier_id: uuid.UUID, reason: str | None = None
) -> Dossier:
    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise ValueError("Dossier not found")

    old_status = dossier.status
    dossier.status = DossierStatus.REJECTED.value
    dossier.notes = reason or dossier.notes

    await log_action(
        db, action="dossier.rejected", dossier_id=dossier_id,
        details={"from": old_status, "reason": reason},
    )
    await db.flush()
    return dossier
