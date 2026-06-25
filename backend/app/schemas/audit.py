import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID | None
    entity_id: uuid.UUID | None
    action: str
    actor: str
    details: dict | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
