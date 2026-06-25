import uuid
from datetime import datetime

from pydantic import BaseModel


class RiskFactorResponse(BaseModel):
    code: str
    points: int
    description: str
    category: str
    blocking: bool
    details: dict | None


class RiskAssessmentResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    total_score: int
    classification: str
    factors: list[RiskFactorResponse]
    blocks_approval: bool
    suggested_actions: list[str]
    calculated_at: datetime

    model_config = {"from_attributes": True}
