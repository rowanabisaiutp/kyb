from datetime import date

from app.models.document import Document
from app.models.fiscal_check import FiscalListCheck
from app.utils.date_utils import is_current_month, is_expired, is_older_than_months


def check_document_expiration(doc: Document) -> bool:
    if doc.fecha_vencimiento and is_expired(doc.fecha_vencimiento):
        return True
    return False


def check_csf_current_month(documents: list[Document]) -> bool:
    for doc in documents:
        if doc.document_type == "constancia_situacion_fiscal" and doc.extracted_data:
            fecha_str = doc.extracted_data.get("fecha_emision") or ""
            if fecha_str:
                from app.utils.date_utils import safe_parse_date
                fecha = safe_parse_date(fecha_str)
                if fecha and is_current_month(fecha):
                    return True
            if doc.fecha_emision and is_current_month(doc.fecha_emision):
                return True
    return False


def check_fiscal_staleness(fiscal_checks: list[FiscalListCheck]) -> bool:
    if not fiscal_checks:
        return True
    latest = max(fc.checked_at for fc in fiscal_checks)
    return is_older_than_months(latest.date() if hasattr(latest, "date") else latest, 3)


def get_expired_documents(documents: list[Document]) -> list[Document]:
    return [d for d in documents if check_document_expiration(d)]


def needs_update(documents: list[Document], fiscal_checks: list[FiscalListCheck]) -> bool:
    if any(check_document_expiration(d) for d in documents):
        return True
    if not check_csf_current_month(documents):
        return True
    if check_fiscal_staleness(fiscal_checks):
        return True
    return False
