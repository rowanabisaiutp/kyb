import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class DossierStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    SAFE = "safe"
    REVIEW_REQUIRED = "review_required"
    HIGH_RISK = "high_risk"
    NEEDS_UPDATE = "needs_update"
    APPROVED = "approved"
    REJECTED = "rejected"


class Dossier(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dossiers"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default=DossierStatus.DRAFT.value, nullable=False)
    current_risk_score: Mapped[int | None] = mapped_column()
    current_risk_classification: Mapped[str | None] = mapped_column(String(20))
    approved_by: Mapped[str | None] = mapped_column(String(200))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column()

    entity: Mapped["LegalEntity"] = relationship(back_populates="dossiers")  # noqa: F821
    documents: Mapped[list["Document"]] = relationship(back_populates="dossier", cascade="all, delete-orphan")  # noqa: F821
    fiscal_checks: Mapped[list["FiscalListCheck"]] = relationship(back_populates="dossier", cascade="all, delete-orphan")  # noqa: F821
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(back_populates="dossier", cascade="all, delete-orphan")  # noqa: F821
    reconciliation_results: Mapped[list["ReconciliationResult"]] = relationship(back_populates="dossier", cascade="all, delete-orphan")  # noqa: F821
