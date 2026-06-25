import enum
import uuid
from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class DocumentType(str, enum.Enum):
    ACTA_CONSTITUTIVA = "acta_constitutiva"
    IDENTIFICACION_REPRESENTANTE = "identificacion_representante"
    PODER_REPRESENTACION = "poder_representacion"
    COMPROBANTE_DOMICILIO = "comprobante_domicilio"
    CONSTANCIA_SITUACION_FISCAL = "constancia_situacion_fiscal"
    MANIFESTACION_PROTESTA = "manifestacion_protesta"
    RFC_DOCUMENTO = "rfc_documento"
    OTRO = "otro"


class ExtractionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    dossier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(500))
    file_key: Mapped[str | None] = mapped_column(String(500))
    file_size: Mapped[int | None] = mapped_column()
    mime_type: Mapped[str | None] = mapped_column(String(100))
    fecha_emision: Mapped[date | None] = mapped_column()
    fecha_vencimiento: Mapped[date | None] = mapped_column()
    is_expired: Mapped[bool] = mapped_column(default=False)
    extracted_data: Mapped[dict | None] = mapped_column(JSON)
    extraction_status: Mapped[str] = mapped_column(
        String(20), default=ExtractionStatus.PENDING.value
    )

    dossier: Mapped["Dossier"] = relationship(back_populates="documents")  # noqa: F821
