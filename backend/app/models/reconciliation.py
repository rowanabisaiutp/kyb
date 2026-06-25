import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class ReconciliationResult(UUIDMixin, Base):
    __tablename__ = "reconciliation_results"

    dossier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_a: Mapped[str] = mapped_column(String(100), nullable=False)
    source_b: Mapped[str] = mapped_column(String(100), nullable=False)
    value_a: Mapped[str | None] = mapped_column()
    value_b: Mapped[str | None] = mapped_column()
    match: Mapped[bool] = mapped_column(nullable=False)
    severity: Mapped[str | None] = mapped_column(String(20))
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    dossier: Mapped["Dossier"] = relationship(back_populates="reconciliation_results")  # noqa: F821
