import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class RiskAssessment(UUIDMixin, Base):
    __tablename__ = "risk_assessments"

    dossier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False
    )
    total_score: Mapped[int] = mapped_column(nullable=False)
    classification: Mapped[str] = mapped_column(String(20), nullable=False)
    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    blocks_approval: Mapped[bool] = mapped_column(default=False)
    suggested_actions: Mapped[dict | None] = mapped_column(JSON)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    dossier: Mapped["Dossier"] = relationship(back_populates="risk_assessments")  # noqa: F821
