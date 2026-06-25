import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.entity import EntityListResponse


class DossierCreate(BaseModel):
    entity_id: uuid.UUID
    notes: str | None = None


class DossierStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(in_review|approved|rejected|needs_update)$")
    approved_by: str | None = None
    notes: str | None = None


class DossierResponse(BaseModel):
    id: uuid.UUID
    entity_id: uuid.UUID
    status: str
    current_risk_score: int | None
    current_risk_classification: str | None
    approved_by: str | None
    approved_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    entity: EntityListResponse | None = None

    model_config = {"from_attributes": True}


class DossierListResponse(BaseModel):
    id: uuid.UUID
    entity_id: uuid.UUID
    status: str
    current_risk_score: int | None
    current_risk_classification: str | None
    created_at: datetime
    updated_at: datetime
    entity: EntityListResponse | None = None

    model_config = {"from_attributes": True}
