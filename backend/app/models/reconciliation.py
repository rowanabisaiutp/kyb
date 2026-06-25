import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


# Conciliacion: compara un campo entre dos fuentes (CSF vs acta, formulario vs poder, etc.).
# Discrepancias alimentan el score: RFC mismatch = +35 bloqueante, razon social = +30.
class ReconciliationResult(UUIDMixin, Base):
    __tablename__ = "reconciliation_results"

    dossier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False
    )
    # Campo comparado: rfc, razon_social, domicilio, representante_legal, fechas.
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Fuentes: "formulario", "constancia_situacion_fiscal", "acta_constitutiva", etc.
    source_a: Mapped[str] = mapped_column(String(100), nullable=False)
    source_b: Mapped[str] = mapped_column(String(100), nullable=False)
    value_a: Mapped[str | None] = mapped_column()
    value_b: Mapped[str | None] = mapped_column()
    match: Mapped[bool] = mapped_column(nullable=False)
    # critical (RFC), warning (razon social, domicilio, rep legal), info (fechas).
    severity: Mapped[str | None] = mapped_column(String(20))
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    dossier: Mapped["Dossier"] = relationship(back_populates="reconciliation_results")  # noqa: F821
