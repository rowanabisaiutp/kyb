from dataclasses import dataclass

from app.models.document import Document
from app.models.entity import LegalEntity
from app.models.fiscal_check import FiscalListCheck
from app.models.reconciliation import ReconciliationResult
from app.services.risk_rules import (
    ART_69B_SITUATION_RULES,
    DOC_EXPIRED_POINTS,
    DOC_MISSING_RULES,
    FISCAL_RULES,
    RECON_RULES,
    SUGGESTED_ACTIONS,
)
from app.services.validity_service import (
    check_csf_current_month,
    check_fiscal_staleness,
    get_expired_documents,
)


@dataclass
class RiskFactor:
    code: str
    points: int
    description: str
    category: str
    blocking: bool
    details: dict | None = None


@dataclass
class RiskAssessmentResult:
    total_score: int
    classification: str
    factors: list[RiskFactor]
    blocks_approval: bool
    suggested_actions: list[str]


# CLASIFICACION: safe (<20) | review_required (20-49) | high_risk (>=50 o bloqueante).
def classify(total_score: int, has_blocking: bool) -> str:
    if has_blocking:
        return "high_risk"
    if total_score >= 50:
        return "high_risk"
    if total_score >= 20:
        return "review_required"
    return "safe"


# PUNTO CENTRAL: calcula score sumando factores de 4 categorias.
# Entrada: entity + docs + fiscal_checks + reconciliation. Salida: score + clasificacion + factores.
def calculate_risk(
    *,
    entity: LegalEntity,
    documents: list[Document],
    fiscal_checks: list[FiscalListCheck],
    reconciliation_results: list[ReconciliationResult],
) -> RiskAssessmentResult:
    factors: list[RiskFactor] = []

    _evaluate_fiscal_rules(
        fiscal_checks, factors
    )  # Listas SAT (Art. 69/69-B/69-B Bis/49 Bis).
    _evaluate_document_rules(
        documents, factors
    )  # Faltantes, vencidos, CSF fuera de mes.
    _evaluate_reconciliation_rules(
        reconciliation_results, factors
    )  # Discrepancias entre docs.
    _evaluate_completeness_rules(entity, factors)  # RFC, rep legal, socios.

    total_score = sum(f.points for f in factors)
    has_blocking = any(f.blocking for f in factors)
    classification = classify(total_score, has_blocking)

    actions = []
    for f in factors:
        if f.points > 0:
            action = SUGGESTED_ACTIONS.get(f.code)
            if action and action not in actions:
                actions.append(action)

    return RiskAssessmentResult(
        total_score=total_score,
        classification=classification,
        factors=factors,
        blocks_approval=has_blocking,
        suggested_actions=actions,
    )


def _evaluate_fiscal_rules(
    fiscal_checks: list[FiscalListCheck], factors: list[RiskFactor]
) -> None:
    if not fiscal_checks:
        factors.append(
            RiskFactor(
                code="FISCAL_NEVER_CHECKED",
                points=25,
                description="Listas fiscales nunca consultadas",
                category="fiscal",
                blocking=False,
            )
        )
        return

    if check_fiscal_staleness(fiscal_checks):
        factors.append(
            RiskFactor(
                code="FISCAL_CHECK_STALE",
                points=15,
                description="Revision de listas fiscales con mas de 3 meses",
                category="fiscal",
                blocking=False,
            )
        )

    found_checks = [fc for fc in fiscal_checks if fc.found]
    processed_types: set[str] = set()

    for fc in found_checks:
        if fc.list_type == "art_69b":
            _evaluate_69b_check(fc, factors, processed_types)
        elif fc.list_type == "art_49bis":
            _evaluate_49bis_check(fc, factors, processed_types)
        elif fc.list_type in FISCAL_RULES and fc.list_type not in processed_types:
            points, blocking, desc = FISCAL_RULES[fc.list_type]
            code = f"FISCAL_{fc.list_type.upper().replace('ART_', '')}"
            factors.append(
                RiskFactor(
                    code=code,
                    points=points,
                    description=desc,
                    category="fiscal",
                    blocking=blocking,
                    details={"list_type": fc.list_type, "source_url": fc.source_url},
                )
            )
            processed_types.add(fc.list_type)


def _extract_69b_situation(fc: FiscalListCheck) -> str | None:
    if not fc.result_detail:
        return None
    details = (
        fc.result_detail
        if isinstance(fc.result_detail, list)
        else [fc.result_detail]
    )
    for row in details:
        if isinstance(row, dict):
            for key in ("Situacion", "Situacion del contribuyente", "SITUACION"):
                if key in row:
                    return row[key].strip()
    return None


def _evaluate_69b_check(
    fc: FiscalListCheck, factors: list[RiskFactor], processed: set[str]
) -> None:
    if "art_69b" in processed:
        return
    processed.add("art_69b")

    situation = _extract_69b_situation(fc)

    if situation:
        for sit_key, (code, points, blocking, desc) in ART_69B_SITUATION_RULES.items():
            if sit_key.lower() in situation.lower():
                factors.append(
                    RiskFactor(
                        code=code,
                        points=points,
                        description=desc,
                        category="fiscal",
                        blocking=blocking,
                        details={"situation": situation},
                    )
                )
                return

    factors.append(
        RiskFactor(
            code="FISCAL_69B_DEFINITIVO",
            points=50,
            description="Encontrado en lista Art. 69-B CFF (situacion no determinada)",
            category="fiscal",
            blocking=True,
            details={"situation": situation or "unknown"},
        )
    )


def _evaluate_49bis_check(
    fc: FiscalListCheck, factors: list[RiskFactor], processed: set[str]
) -> None:
    if "art_49bis" in processed:
        return
    processed.add("art_49bis")

    if "art_69b" in processed:
        factors.append(
            RiskFactor(
                code="FISCAL_49BIS",
                points=0,
                description="Art. 49 Bis CFF: cubierto por hallazgo en Art. 69-B (misma fuente publica del SAT)",
                category="fiscal",
                blocking=False,
                details={
                    "source_url": fc.source_url,
                    "justification": "El listado Art. 69-B del SAT es la unica fuente publica disponible para Art. 49 Bis CFF. El riesgo ya se contabiliza en la regla Art. 69-B.",
                },
            )
        )
        return

    factors.append(
        RiskFactor(
            code="FISCAL_49BIS",
            points=45,
            description="Operaciones con EFOS (Art. 49 Bis CFF)",
            category="fiscal",
            blocking=True,
            details={
                "source_url": fc.source_url,
                "justification": "Fuente: listado Art. 69-B del SAT, unica base publica disponible para Art. 49 Bis CFF.",
            },
        )
    )


def _evaluate_document_rules(
    documents: list[Document], factors: list[RiskFactor]
) -> None:
    present_types = {d.document_type for d in documents}

    for doc_type, (code, points, desc) in DOC_MISSING_RULES.items():
        if doc_type not in present_types:
            factors.append(
                RiskFactor(
                    code=code,
                    points=points,
                    description=desc,
                    category="documents",
                    blocking=False,
                )
            )

    for doc in get_expired_documents(documents):
        pts = DOC_EXPIRED_POINTS.get(doc.document_type, 15)
        factors.append(
            RiskFactor(
                code="DOC_EXPIRED",
                points=pts,
                description=f"Documento vencido: {doc.document_type}",
                category="documents",
                blocking=False,
                details={
                    "document_type": doc.document_type,
                    "fecha_vencimiento": str(doc.fecha_vencimiento),
                },
            )
        )

    if (
        not check_csf_current_month(documents)
        and "constancia_situacion_fiscal" in present_types
    ):
        factors.append(
            RiskFactor(
                code="CSF_NOT_CURRENT_MONTH",
                points=15,
                description="Constancia de situacion fiscal no es del mes vigente",
                category="documents",
                blocking=False,
            )
        )


def _evaluate_reconciliation_rules(
    results: list[ReconciliationResult], factors: list[RiskFactor]
) -> None:
    discrepancy_fields: set[str] = set()
    for r in results:
        if not r.match and r.field_name not in discrepancy_fields:
            rule = RECON_RULES.get(r.field_name)
            if rule:
                code, points, blocking, desc = rule
                factors.append(
                    RiskFactor(
                        code=code,
                        points=points,
                        description=desc,
                        category="reconciliation",
                        blocking=blocking,
                        details={
                            "source_a": r.source_a,
                            "source_b": r.source_b,
                            "value_a": r.value_a,
                            "value_b": r.value_b,
                        },
                    )
                )
                discrepancy_fields.add(r.field_name)


# --- Reglas completitud: RFC, representante legal, socios/accionistas ---
def _evaluate_completeness_rules(
    entity: LegalEntity, factors: list[RiskFactor]
) -> None:
    if not entity.rfc:
        factors.append(
            RiskFactor(
                code="COMP_RFC_MISSING",
                points=25,
                description="RFC no registrado",
                category="completeness",
                blocking=True,
            )
        )

    if not entity.representatives:
        factors.append(
            RiskFactor(
                code="COMP_NO_REP_LEGAL",
                points=20,
                description="Sin representante legal registrado",
                category="completeness",
                blocking=False,
            )
        )

    if not entity.shareholders:
        factors.append(
            RiskFactor(
                code="COMP_NO_SHAREHOLDERS",
                points=10,
                description="Sin socios o accionistas registrados",
                category="completeness",
                blocking=False,
            )
        )
