import uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models.dossier import Dossier
from app.models.entity import LegalEntity
from app.models.fiscal_check import FiscalListCheck
from app.models.reconciliation import ReconciliationResult
from app.models.risk import RiskAssessment
from app.schemas.risk import RiskAssessmentResponse
from app.services.audit_service import log_action
from app.services.document_service import list_documents
from app.services.risk_engine import calculate_risk

router = APIRouter(tags=["risk"])


async def _fetch_risk_inputs(
    db: AsyncSession, dossier_id: uuid.UUID, dossier: Dossier
):
    result = await db.execute(
        select(LegalEntity)
        .where(LegalEntity.id == dossier.entity_id)
        .options(
            selectinload(LegalEntity.representatives),
            selectinload(LegalEntity.shareholders),
        )
    )
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    documents = await list_documents(db, dossier_id)

    fiscal_result = await db.execute(
        select(FiscalListCheck).where(FiscalListCheck.dossier_id == dossier_id)
    )
    fiscal_checks = list(fiscal_result.scalars().all())

    recon_result = await db.execute(
        select(ReconciliationResult).where(
            ReconciliationResult.dossier_id == dossier_id
        )
    )
    reconciliation_results = list(recon_result.scalars().all())

    return entity, documents, fiscal_checks, reconciliation_results


async def _persist_assessment(
    db: AsyncSession, dossier_id: uuid.UUID, dossier: Dossier, assessment
):
    factors_data = [asdict(f) for f in assessment.factors]

    risk_record = RiskAssessment(
        dossier_id=dossier_id,
        total_score=assessment.total_score,
        classification=assessment.classification,
        factors=factors_data,
        blocks_approval=assessment.blocks_approval,
        suggested_actions=assessment.suggested_actions,
    )
    db.add(risk_record)

    dossier.current_risk_score = assessment.total_score
    dossier.current_risk_classification = assessment.classification

    await db.flush()

    await log_action(
        db,
        action="risk.calculated",
        dossier_id=dossier_id,
        details={
            "total_score": assessment.total_score,
            "classification": assessment.classification,
            "blocks_approval": assessment.blocks_approval,
            "factors_count": len(assessment.factors),
        },
    )

    await db.commit()
    await db.refresh(risk_record)
    return risk_record, factors_data


def _to_response(
    record: RiskAssessment, factors_data: list, suggested_actions: list
) -> RiskAssessmentResponse:
    return RiskAssessmentResponse(
        id=record.id,
        dossier_id=record.dossier_id,
        total_score=record.total_score,
        classification=record.classification,
        factors=factors_data,
        blocks_approval=record.blocks_approval,
        suggested_actions=suggested_actions,
        calculated_at=record.calculated_at,
    )


@router.post(
    "/dossiers/{dossier_id}/risk-assessment", response_model=RiskAssessmentResponse
)
async def calculate_dossier_risk(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    entity, documents, fiscal_checks, reconciliation_results = (
        await _fetch_risk_inputs(db, dossier_id, dossier)
    )

    assessment = calculate_risk(
        entity=entity,
        documents=documents,
        fiscal_checks=fiscal_checks,
        reconciliation_results=reconciliation_results,
    )

    record, factors_data = await _persist_assessment(
        db, dossier_id, dossier, assessment
    )
    return _to_response(record, factors_data, assessment.suggested_actions)


@router.get(
    "/dossiers/{dossier_id}/risk-assessments",
    response_model=list[RiskAssessmentResponse],
)
async def list_risk_assessments(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.dossier_id == dossier_id)
        .order_by(RiskAssessment.calculated_at.desc())
    )
    records = result.scalars().all()
    return [
        RiskAssessmentResponse(
            id=r.id,
            dossier_id=r.dossier_id,
            total_score=r.total_score,
            classification=r.classification,
            factors=r.factors if isinstance(r.factors, list) else [],
            blocks_approval=r.blocks_approval,
            suggested_actions=r.suggested_actions
            if isinstance(r.suggested_actions, list)
            else [],
            calculated_at=r.calculated_at,
        )
        for r in records
    ]


@router.get(
    "/dossiers/{dossier_id}/risk-assessment/latest",
    response_model=RiskAssessmentResponse | None,
)
async def get_latest_risk_assessment(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.dossier_id == dossier_id)
        .order_by(RiskAssessment.calculated_at.desc())
        .limit(1)
    )
    r = result.scalar_one_or_none()
    if not r:
        return None
    return RiskAssessmentResponse(
        id=r.id,
        dossier_id=r.dossier_id,
        total_score=r.total_score,
        classification=r.classification,
        factors=r.factors if isinstance(r.factors, list) else [],
        blocks_approval=r.blocks_approval,
        suggested_actions=r.suggested_actions
        if isinstance(r.suggested_actions, list)
        else [],
        calculated_at=r.calculated_at,
    )


async def _build_summary_data(
    db: AsyncSession, dossier_id: uuid.UUID, dossier: Dossier
) -> dict:
    from app.services.document_service import get_missing_documents

    entity_result = await db.execute(
        select(LegalEntity).where(LegalEntity.id == dossier.entity_id)
    )
    entity = entity_result.scalar_one_or_none()

    fiscal_result = await db.execute(
        select(FiscalListCheck).where(FiscalListCheck.dossier_id == dossier_id)
    )
    fiscal_checks = fiscal_result.scalars().all()

    recon_result = await db.execute(
        select(ReconciliationResult).where(
            ReconciliationResult.dossier_id == dossier_id
        )
    )
    reconciliation = recon_result.scalars().all()

    documents = await list_documents(db, dossier_id)

    return {
        "empresa": entity.razon_social if entity else "",
        "rfc": entity.rfc if entity else "",
        "status": dossier.status,
        "risk_score": dossier.current_risk_score,
        "risk_classification": dossier.current_risk_classification,
        "documentos_cargados": len(documents),
        "documentos_faltantes": get_missing_documents(documents),
        "listas_fiscales_encontrado": sum(1 for fc in fiscal_checks if fc.found),
        "listas_fiscales_total": len(list(fiscal_checks)),
        "discrepancias": sum(1 for r in reconciliation if not r.match),
    }


@router.get("/dossiers/{dossier_id}/summary")
async def get_dossier_summary(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    from app.services.summary_service import generate_dossier_summary

    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    dossier_data = await _build_summary_data(db, dossier_id, dossier)
    summary = await generate_dossier_summary(dossier_data)
    if not summary:
        raise HTTPException(status_code=503, detail="Summary service unavailable")
    return summary
