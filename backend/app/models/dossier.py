import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


# Clasificacion: safe | review_required | high_risk (score de riesgo).
# Vigencias: needs_update cuando doc vence, CSF fuera de mes, o fiscal > 3 meses.
class DossierStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    SAFE = "safe"  # Score < 20, sin bloqueantes.
    REVIEW_REQUIRED = "review_required"  # Score 20-49, sin bloqueantes.
    HIGH_RISK = "high_risk"  # Score >= 50 o factor bloqueante. Aprobacion bloqueada.
    NEEDS_UPDATE = "needs_update"  # Vigencia caducada, scheduler automatico cada hora.
    APPROVED = "approved"
    REJECTED = "rejected"


# Expediente electronico KYB (Regla 1.4.14 RGCE). Uno por persona moral.
class Dossier(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dossiers"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default=DossierStatus.DRAFT.value, nullable=False
    )
    # Ultimo score calculado por risk_engine.calculate_risk().
    current_risk_score: Mapped[int | None] = mapped_column()
    # safe | review_required | high_risk (determinado por classify()).
    current_risk_classification: Mapped[str | None] = mapped_column(String(20))
    approved_by: Mapped[str | None] = mapped_column(String(200))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column()

    entity: Mapped["LegalEntity"] = relationship(back_populates="dossiers")  # noqa: F821
    documents: Mapped[list["Document"]] = relationship(
        back_populates="dossier", cascade="all, delete-orphan"
    )  # noqa: F821
    fiscal_checks: Mapped[list["FiscalListCheck"]] = relationship(
        back_populates="dossier", cascade="all, delete-orphan"
    )  # noqa: F821
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="dossier", cascade="all, delete-orphan"
    )  # noqa: F821
    reconciliation_results: Mapped[list["ReconciliationResult"]] = relationship(
        back_populates="dossier", cascade="all, delete-orphan"
    )  # noqa: F821
