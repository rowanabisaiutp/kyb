from dataclasses import dataclass

from app.models.document import Document
from app.models.entity import LegalEntity
from app.models.fiscal_check import FiscalListCheck
from app.models.reconciliation import ReconciliationResult
from app.services.validity_service import (
    check_csf_current_month,
    check_fiscal_staleness,
    get_expired_documents,
)


# SCORE DE RIESGO — determinístico, explicable, testeable.
# Funcion pura: sin DB, sin side effects, sin aleatoriedad. Misma entrada = mismo resultado.
# Evalua 4 categorias: fiscal, documentos, conciliacion, completitud.
# Cada factor tiene code, points, description, blocking y suggested_action.
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


# --- Reglas fiscales: Art. 69, 69-B, 69-B Bis, 49 Bis CFF ---
# Cada regla: (puntos, bloqueante, descripcion).

FISCAL_RULES: dict[str, tuple[int, bool, str]] = {
    "art_69_firmes": (40, True, "Creditos fiscales firmes (Art. 69 CFF)"),
    "art_69_exigibles": (35, False, "Creditos fiscales exigibles (Art. 69 CFF)"),
    "art_69_no_localizados": (50, True, "Contribuyente no localizado (Art. 69 CFF)"),
    "art_69_sentencias": (
        30,
        False,
        "Sentencia condenatoria por delito fiscal (Art. 69 CFF)",
    ),
    "art_69_cancelados": (25, False, "Creditos fiscales cancelados (Art. 69 CFF)"),
    "art_69_csd_sin_efectos": (40, True, "CSD sin efectos (Art. 69 CFF)"),
    "art_69b_bis": (45, True, "Transmision indebida de perdidas (Art. 69-B Bis CFF)"),
}

# Art. 69-B: score varia segun situacion (Definitivo/Presunto/Desvirtuado/Sentencia).
ART_69B_SITUATION_RULES: dict[str, tuple[str, int, bool, str]] = {
    "Definitivo": (
        "FISCAL_69B_DEFINITIVO",
        50,
        True,
        "EFOS definitivo (Art. 69-B CFF)",
    ),
    "Presunto": ("FISCAL_69B_PRESUNTO", 40, True, "EFOS presunto (Art. 69-B CFF)"),
    "Desvirtuado": (
        "FISCAL_69B_DESVIRTUADO",
        5,
        False,
        "EFOS desvirtuado (Art. 69-B CFF)",
    ),
    "Sentencia Favorable": (
        "FISCAL_69B_SENTENCIA_FAV",
        0,
        False,
        "EFOS con sentencia favorable (Art. 69-B CFF)",
    ),
}

# --- Reglas documentos: faltantes y vencidos ---
DOC_MISSING_RULES: dict[str, tuple[str, int, str]] = {
    "acta_constitutiva": ("DOC_MISSING_ACTA", 15, "Acta constitutiva faltante"),
    "identificacion_representante": (
        "DOC_MISSING_ID_REP",
        15,
        "Identificacion del representante faltante",
    ),
    "comprobante_domicilio": (
        "DOC_MISSING_COMPROBANTE",
        10,
        "Comprobante de domicilio faltante",
    ),
    "constancia_situacion_fiscal": (
        "DOC_MISSING_CSF",
        20,
        "Constancia de situacion fiscal faltante",
    ),
    "manifestacion_protesta": (
        "DOC_MISSING_MANIFESTACION",
        10,
        "Manifestacion bajo protesta faltante",
    ),
}

# Docs vencidos: comprobante/ID +20, otros +15.
DOC_EXPIRED_POINTS: dict[str, int] = {
    "comprobante_domicilio": 20,
    "identificacion_representante": 20,
}

# --- Reglas conciliacion: discrepancias entre documentos ---
# RFC mismatch es bloqueante (+35). Razon social +30. Domicilio +15.
RECON_RULES: dict[str, tuple[str, int, bool, str]] = {
    "rfc": ("RECON_RFC_MISMATCH", 35, True, "Discrepancia de RFC entre documentos"),
    "razon_social": (
        "RECON_RAZON_SOCIAL_MISMATCH",
        30,
        False,
        "Discrepancia de razon social entre documentos",
    ),
    "domicilio": (
        "RECON_DOMICILIO_MISMATCH",
        15,
        False,
        "Discrepancia de domicilio entre documentos",
    ),
    "representante_legal": (
        "RECON_REP_LEGAL_MISMATCH",
        25,
        False,
        "Discrepancia de representante legal entre documentos",
    ),
    "fecha_emision": (
        "RECON_FECHA_EMISION_MISMATCH",
        10,
        False,
        "Discrepancia de fecha de emision entre documentos",
    ),
    "fecha_constitucion": (
        "RECON_FECHA_CONSTITUCION_MISMATCH",
        5,
        False,
        "Discrepancia de fecha de constitucion entre documentos",
    ),
}

# --- Acciones sugeridas: texto en español por cada factor detectado ---
SUGGESTED_ACTIONS: dict[str, str] = {
    "FISCAL_69_FIRMES": "Resolver creditos fiscales firmes ante el SAT",
    "FISCAL_69_EXIGIBLES": "Atender creditos fiscales exigibles",
    "FISCAL_69_NO_LOCALIZADOS": "Actualizar domicilio fiscal ante el SAT",
    "FISCAL_69_SENTENCIAS": "Revisar situacion legal del contribuyente",
    "FISCAL_69_CANCELADOS": "Verificar estado de creditos cancelados",
    "FISCAL_69_CSD_SIN_EFECTOS": "Regularizar CSD ante el SAT",
    "FISCAL_69B_DEFINITIVO": "CRITICO: Contribuyente en lista de EFOS definitivos. No operar.",
    "FISCAL_69B_PRESUNTO": "Verificar situacion de EFOS presunto urgentemente",
    "FISCAL_69B_DESVIRTUADO": "Documentar evidencia de desvirtuacion de EFOS",
    "FISCAL_69B_BIS": "Revisar operacion por transmision indebida de perdidas",
    "FISCAL_49BIS": "Verificar operaciones con contribuyentes EFOS (Art. 49 Bis CFF)",
    "FISCAL_CHECK_STALE": "Actualizar consulta de listas fiscales del SAT",
    "FISCAL_NEVER_CHECKED": "Ejecutar consulta de listas fiscales del SAT",
    "DOC_MISSING_ACTA": "Cargar acta constitutiva",
    "DOC_MISSING_ID_REP": "Cargar identificacion del representante legal",
    "DOC_MISSING_COMPROBANTE": "Cargar comprobante de domicilio vigente",
    "DOC_MISSING_CSF": "Cargar constancia de situacion fiscal del mes actual",
    "DOC_MISSING_MANIFESTACION": "Cargar manifestacion bajo protesta de decir verdad",
    "DOC_EXPIRED": "Actualizar documento vencido",
    "CSF_NOT_CURRENT_MONTH": "Obtener constancia de situacion fiscal del mes vigente",
    "RECON_RFC_MISMATCH": "CRITICO: Corregir discrepancia de RFC entre documentos",
    "RECON_RAZON_SOCIAL_MISMATCH": "Corregir razon social para que coincida entre documentos",
    "RECON_DOMICILIO_MISMATCH": "Verificar y corregir domicilio entre documentos",
    "RECON_REP_LEGAL_MISMATCH": "Verificar datos del representante legal entre documentos",
    "COMP_NO_REP_LEGAL": "Registrar representante legal del expediente",
    "COMP_NO_SHAREHOLDERS": "Registrar socios o accionistas",
    "COMP_RFC_MISSING": "Registrar RFC de la persona moral",
    "RECON_FECHA_EMISION_MISMATCH": "Verificar fechas de emision entre documentos",
    "RECON_FECHA_CONSTITUCION_MISMATCH": "Verificar fecha de constitucion en el acta",
}


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

    _evaluate_fiscal_rules(fiscal_checks, factors)       # Listas SAT (Art. 69/69-B/69-B Bis/49 Bis).
    _evaluate_document_rules(documents, factors)          # Faltantes, vencidos, CSF fuera de mes.
    _evaluate_reconciliation_rules(reconciliation_results, factors)  # Discrepancias entre docs.
    _evaluate_completeness_rules(entity, factors)         # RFC, rep legal, socios.

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


def _evaluate_69b_check(
    fc: FiscalListCheck, factors: list[RiskFactor], processed: set[str]
) -> None:
    if "art_69b" in processed:
        return
    processed.add("art_69b")

    situation = None
    if fc.result_detail:
        details = (
            fc.result_detail
            if isinstance(fc.result_detail, list)
            else [fc.result_detail]
        )
        for row in details:
            if isinstance(row, dict):
                for key in ("Situacion", "Situacion del contribuyente", "SITUACION"):
                    if key in row:
                        situation = row[key].strip()
                        break
            if situation:
                break

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
