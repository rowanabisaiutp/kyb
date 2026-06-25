import uuid
from datetime import datetime

from pydantic import BaseModel


class ReconciliationResultResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    field_name: str
    source_a: str
    source_b: str
    value_a: str | None
    value_b: str | None
    match: bool
    severity: str | None
    checked_at: datetime

    model_config = {"from_attributes": True}


class ReconciliationSummary(BaseModel):
    total_comparisons: int
    matches: int
    discrepancies: int
    has_critical: bool
    results: list[ReconciliationResultResponse]
