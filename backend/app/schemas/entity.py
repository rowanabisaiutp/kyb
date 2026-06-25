import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class LegalRepresentativeCreate(BaseModel):
    nombre_completo: str = Field(..., max_length=500)
    curp: str | None = Field(None, max_length=18)
    rfc_persona_fisica: str | None = Field(None, max_length=13)
    cargo: str | None = Field(None, max_length=200)


class LegalRepresentativeResponse(LegalRepresentativeCreate):
    id: uuid.UUID
    entity_id: uuid.UUID
    vigente: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ShareholderCreate(BaseModel):
    nombre_completo: str = Field(..., max_length=500)
    rfc: str | None = Field(None, max_length=13)
    porcentaje_participacion: Decimal | None = Field(None, ge=0, le=100)
    tipo: str = Field(..., pattern=r"^(socio|accionista|beneficiario_controlador)$")


class ShareholderResponse(ShareholderCreate):
    id: uuid.UUID
    entity_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class EntityCreate(BaseModel):
    rfc: str = Field(..., min_length=12, max_length=13)
    razon_social: str = Field(..., max_length=500)
    nombre_comercial: str | None = Field(None, max_length=500)
    domicilio_fiscal: str | None = None
    codigo_postal: str | None = Field(None, max_length=5)
    regimen_fiscal: str | None = Field(None, max_length=200)
    fecha_constitucion: date | None = None
    objeto_social: str | None = None
    representatives: list[LegalRepresentativeCreate] = Field(default_factory=list)
    shareholders: list[ShareholderCreate] = Field(default_factory=list)


class EntityUpdate(BaseModel):
    razon_social: str | None = Field(None, max_length=500)
    nombre_comercial: str | None = Field(None, max_length=500)
    domicilio_fiscal: str | None = None
    codigo_postal: str | None = Field(None, max_length=5)
    regimen_fiscal: str | None = Field(None, max_length=200)
    fecha_constitucion: date | None = None
    objeto_social: str | None = None


class EntityResponse(BaseModel):
    id: uuid.UUID
    rfc: str
    razon_social: str
    nombre_comercial: str | None
    domicilio_fiscal: str | None
    codigo_postal: str | None
    regimen_fiscal: str | None
    fecha_constitucion: date | None
    objeto_social: str | None
    created_at: datetime
    updated_at: datetime
    representatives: list[LegalRepresentativeResponse] = []
    shareholders: list[ShareholderResponse] = []

    model_config = {"from_attributes": True}


class EntityListResponse(BaseModel):
    id: uuid.UUID
    rfc: str
    razon_social: str
    nombre_comercial: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
