import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.entity import LegalEntity
from app.models.reconciliation import ReconciliationResult
from app.services.audit_service import log_action
from app.utils.text_normalization import (
    business_names_match,
    normalize_address,
    normalize_business_name,
    normalize_text,
    texts_match,
)

FIELD_SEVERITY = {
    "rfc": "critical",
    "razon_social": "warning",
    "domicilio": "warning",
    "representante_legal": "warning",
    "fecha_emision": "info",
    "fecha_constitucion": "info",
}

FIELD_EXTRACTORS: dict[str, dict[str, list[str]]] = {
    "rfc": {
        "constancia_situacion_fiscal": ["rfc"],
        "acta_constitutiva": ["rfc"],
    },
    "razon_social": {
        "constancia_situacion_fiscal": ["razon_social"],
        "acta_constitutiva": ["razon_social"],
    },
    "domicilio": {
        "constancia_situacion_fiscal": ["domicilio_fiscal"],
        "comprobante_domicilio": ["direccion_completa"],
    },
    "representante_legal": {
        "poder_representacion": ["representante_legal"],
        "identificacion_representante": ["nombre_completo"],
    },
    "fecha_emision": {
        "constancia_situacion_fiscal": ["fecha_emision"],
        "comprobante_domicilio": ["fecha_emision"],
    },
    "fecha_constitucion": {
        "acta_constitutiva": ["fecha_constitucion"],
    },
}


def _extract_value(extracted_data: dict | None, keys: list[str]) -> str | None:
    if not extracted_data:
        return None
    for key in keys:
        val = extracted_data.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return None


def _compare_values(field: str, val_a: str | None, val_b: str | None) -> bool:
    if not val_a or not val_b:
        return val_a == val_b

    if field == "rfc":
        return normalize_text(val_a) == normalize_text(val_b)
    if field == "razon_social":
        return business_names_match(val_a, val_b)
    if field == "domicilio":
        return normalize_address(val_a) == normalize_address(val_b) or texts_match(val_a, val_b, threshold=0.7)
    if field in ("fecha_emision", "fecha_constitucion"):
        from app.utils.date_utils import safe_parse_date
        date_a = safe_parse_date(val_a)
        date_b = safe_parse_date(val_b)
        if date_a and date_b:
            return date_a == date_b
        return normalize_text(val_a) == normalize_text(val_b)
    return texts_match(val_a, val_b)


async def run_reconciliation(
    db: AsyncSession,
    *,
    dossier_id: uuid.UUID,
    entity: LegalEntity,
    documents: list[Document],
) -> list[ReconciliationResult]:
    await db.execute(
        delete(ReconciliationResult).where(ReconciliationResult.dossier_id == dossier_id)
    )

    doc_by_type: dict[str, Document] = {}
    for doc in documents:
        if doc.extracted_data and doc.extraction_status == "completed":
            doc_by_type[doc.document_type] = doc

    results: list[ReconciliationResult] = []

    for field_name, sources in FIELD_EXTRACTORS.items():
        available_sources: list[tuple[str, str | None]] = []

        entity_value = _get_entity_value(entity, field_name)
        if entity_value:
            available_sources.append(("formulario", entity_value))

        for doc_type, keys in sources.items():
            doc = doc_by_type.get(doc_type)
            if doc and doc.extracted_data:
                val = _extract_value(doc.extracted_data, keys)
                if val:
                    available_sources.append((doc_type, val))

        for i in range(len(available_sources)):
            for j in range(i + 1, len(available_sources)):
                source_a, value_a = available_sources[i]
                source_b, value_b = available_sources[j]

                match = _compare_values(field_name, value_a, value_b)
                severity = None if match else FIELD_SEVERITY.get(field_name, "info")

                result = ReconciliationResult(
                    dossier_id=dossier_id,
                    field_name=field_name,
                    source_a=source_a,
                    source_b=source_b,
                    value_a=value_a,
                    value_b=value_b,
                    match=match,
                    severity=severity,
                )
                db.add(result)
                results.append(result)

    await db.flush()

    discrepancies = [r for r in results if not r.match]
    await log_action(
        db,
        action="reconciliation.run",
        dossier_id=dossier_id,
        details={
            "total_comparisons": len(results),
            "discrepancies": len(discrepancies),
            "fields_compared": list(FIELD_EXTRACTORS.keys()),
        },
    )

    return results


def _get_entity_value(entity: LegalEntity, field_name: str) -> str | None:
    if field_name == "rfc":
        return entity.rfc
    if field_name == "razon_social":
        return entity.razon_social
    if field_name == "domicilio":
        return entity.domicilio_fiscal
    if field_name == "representante_legal":
        if entity.representatives:
            return entity.representatives[0].nombre_completo
    return None


async def get_reconciliation_results(
    db: AsyncSession, dossier_id: uuid.UUID
) -> list[ReconciliationResult]:
    result = await db.execute(
        select(ReconciliationResult)
        .where(ReconciliationResult.dossier_id == dossier_id)
        .order_by(ReconciliationResult.field_name)
    )
    return list(result.scalars().all())
