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

    assessment = calculate_risk(
        entity=entity,
        documents=documents,
        fiscal_checks=fiscal_checks,
        reconciliation_results=reconciliation_results,
    )

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
    if assessment.classification != dossier.status:
        dossier.status = assessment.classification

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

    return RiskAssessmentResponse(
        id=risk_record.id,
        dossier_id=risk_record.dossier_id,
        total_score=risk_record.total_score,
        classification=risk_record.classification,
        factors=factors_data,
        blocks_approval=risk_record.blocks_approval,
        suggested_actions=assessment.suggested_actions,
        calculated_at=risk_record.calculated_at,
    )


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


@router.get("/dossiers/{dossier_id}/summary")
async def get_dossier_summary(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    from app.services.extraction_service import generate_dossier_summary

    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    entity_result = await db.execute(
        select(LegalEntity).where(LegalEntity.id == dossier.entity_id)
    )
    entity = entity_result.scalar_one_or_none()

    docs_result = await db.execute(
        select(FiscalListCheck).where(FiscalListCheck.dossier_id == dossier_id)
    )
    fiscal_checks = docs_result.scalars().all()

    recon_result = await db.execute(
        select(ReconciliationResult).where(
            ReconciliationResult.dossier_id == dossier_id
        )
    )
    reconciliation = recon_result.scalars().all()

    from app.services.document_service import list_documents, get_missing_documents

    documents = await list_documents(db, dossier_id)
    missing = get_missing_documents(documents)

    dossier_data = {
        "empresa": entity.razon_social if entity else "",
        "rfc": entity.rfc if entity else "",
        "status": dossier.status,
        "risk_score": dossier.current_risk_score,
        "risk_classification": dossier.current_risk_classification,
        "documentos_cargados": len(documents),
        "documentos_faltantes": missing,
        "listas_fiscales_encontrado": sum(1 for fc in fiscal_checks if fc.found),
        "listas_fiscales_total": len(fiscal_checks),
        "discrepancias": sum(1 for r in reconciliation if not r.match),
    }

    summary = await generate_dossier_summary(dossier_data)
    if not summary:
        raise HTTPException(status_code=503, detail="Summary service unavailable")
    return summary
