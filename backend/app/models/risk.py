import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


# Snapshot de una evaluacion de riesgo. Calculado por risk_engine.calculate_risk().
# Historial: se guarda cada calculo para trazabilidad (audit log).
class RiskAssessment(UUIDMixin, Base):
    __tablename__ = "risk_assessments"

    dossier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False
    )
    # Suma de puntos de todos los factores detectados.
    total_score: Mapped[int] = mapped_column(nullable=False)
    # safe (<20) | review_required (20-49) | high_risk (>=50 o bloqueante).
    classification: Mapped[str] = mapped_column(String(20), nullable=False)
    # Lista de factores: {code, points, description, category, blocking, details}.
    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    # True si algun factor es bloqueante -> impide aprobar el expediente.
    blocks_approval: Mapped[bool] = mapped_column(default=False)
    # Acciones correctivas en español por cada factor detectado.
    suggested_actions: Mapped[dict | None] = mapped_column(JSON)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    dossier: Mapped["Dossier"] = relationship(back_populates="risk_assessments")  # noqa: F821
