import uuid
from datetime import datetime

from pydantic import BaseModel


class UUIDResponse(BaseModel):
    id: uuid.UUID


class TimestampResponse(BaseModel):
    created_at: datetime
    updated_at: datetime


class PaginatedRequest(BaseModel):
    skip: int = 0
    limit: int = 50


class ErrorResponse(BaseModel):
    detail: str


class MessageResponse(BaseModel):
    message: str
