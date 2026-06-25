import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


# Req: Registrar evidencia y audit log de todas las acciones del expediente.
async def log_action(
    db: AsyncSession,
    *,
    action: str,
    dossier_id: uuid.UUID | None = None,
    entity_id: uuid.UUID | None = None,
    actor: str = "system",
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        action=action,
        dossier_id=dossier_id,
        entity_id=entity_id,
        actor=actor,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()
    return entry
