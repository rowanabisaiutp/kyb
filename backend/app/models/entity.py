import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


# Regla 1.4.14 RGCE: persona moral sujeta a evaluacion KYB.
class LegalEntity(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "legal_entities"

    # RFC obligatorio; si falta, el score suma +25 bloqueante (COMP_RFC_MISSING).
    rfc: Mapped[str] = mapped_column(
        String(13), unique=True, nullable=False, index=True
    )
    razon_social: Mapped[str] = mapped_column(String(500), nullable=False)
    nombre_comercial: Mapped[str | None] = mapped_column(String(500))
    domicilio_fiscal: Mapped[str | None] = mapped_column()
    codigo_postal: Mapped[str | None] = mapped_column(String(5))
    regimen_fiscal: Mapped[str | None] = mapped_column(String(200))
    fecha_constitucion: Mapped[date | None] = mapped_column()
    objeto_social: Mapped[str | None] = mapped_column()

    # Si no hay representantes -> +20 riesgo (COMP_NO_REP_LEGAL).
    representatives: Mapped[list["LegalRepresentative"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    # Si no hay socios -> +10 riesgo (COMP_NO_SHAREHOLDERS).
    shareholders: Mapped[list["Shareholder"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    dossiers: Mapped[list["Dossier"]] = relationship(back_populates="entity")  # noqa: F821


# Conciliacion: se cruza con poder_representacion e identificacion_representante.
class LegalRepresentative(UUIDMixin, Base):
    __tablename__ = "legal_representatives"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False
    )
    nombre_completo: Mapped[str] = mapped_column(String(500), nullable=False)
    curp: Mapped[str | None] = mapped_column(String(18))
    rfc_persona_fisica: Mapped[str | None] = mapped_column(String(13))
    cargo: Mapped[str | None] = mapped_column(String(200))
    vigente: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    entity: Mapped["LegalEntity"] = relationship(back_populates="representatives")


# Socios/accionistas/beneficiario controlador (Regla 1.4.14 RGCE).
class Shareholder(UUIDMixin, Base):
    __tablename__ = "shareholders"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False
    )
    nombre_completo: Mapped[str] = mapped_column(String(500), nullable=False)
    rfc: Mapped[str | None] = mapped_column(String(13))
    porcentaje_participacion: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    entity: Mapped["LegalEntity"] = relationship(back_populates="shareholders")
