import uuid
from datetime import datetime

from pydantic import BaseModel


class FiscalCheckResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    rfc_searched: str
    list_type: str
    source_url: str
    checked_at: datetime
    found: bool
    result_detail: dict | list | None
    list_reference: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FiscalCheckSummary(BaseModel):
    total_lists_checked: int
    matches_found: int
    clean: bool
    checks: list[FiscalCheckResponse]


class FiscalListsStatus(BaseModel):
    loaded: bool
    last_loaded: str | None
    lists_count: int
    lists: dict
