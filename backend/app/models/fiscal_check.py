import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class FiscalListCheck(UUIDMixin, Base):
    __tablename__ = "fiscal_list_checks"

    dossier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False
    )
    rfc_searched: Mapped[str] = mapped_column(String(13), nullable=False)
    list_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str] = mapped_column(nullable=False)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    found: Mapped[bool] = mapped_column(nullable=False)
    result_detail: Mapped[dict | None] = mapped_column(JSON)
    list_reference: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    dossier: Mapped["Dossier"] = relationship(back_populates="fiscal_checks")  # noqa: F821
