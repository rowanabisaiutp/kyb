import uuid
from datetime import date, datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    document_type: str
    file_name: str | None
    file_key: str | None
    file_size: int | None
    mime_type: str | None
    fecha_emision: date | None
    fecha_vencimiento: date | None
    is_expired: bool
    extracted_data: dict | None
    extraction_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    id: uuid.UUID
    document_type: str
    file_name: str | None
    file_size: int | None
    mime_type: str | None
    fecha_emision: date | None
    fecha_vencimiento: date | None
    is_expired: bool
    extraction_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MissingDocumentsResponse(BaseModel):
    missing: list[str]
    total_required: int
    total_present: int
