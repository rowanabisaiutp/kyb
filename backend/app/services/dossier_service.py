import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dossier import Dossier, DossierStatus
from app.models.fiscal_check import FiscalListCheck
from app.services.audit_service import log_action
from app.services.document_service import list_documents
from app.services.validity_service import needs_update


# VIGENCIAS AUTOMATICAS: llamado por el scheduler cada hora (main.py).
# Evalua los 3 triggers y cambia status a needs_update si aplica.
async def check_and_update_validity(
    db: AsyncSession, dossier_id: uuid.UUID
) -> str | None:
    dossier = await db.get(Dossier, dossier_id)
    if not dossier or dossier.status in (
        DossierStatus.DRAFT.value,
        DossierStatus.REJECTED.value,
    ):
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
                db,
                action="dossier.auto_needs_update",
                dossier_id=dossier_id,
                details={"from": old_status, "to": DossierStatus.NEEDS_UPDATE.value},
            )
            await db.flush()
            return DossierStatus.NEEDS_UPDATE.value

    return dossier.status
