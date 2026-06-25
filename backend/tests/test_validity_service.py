from datetime import date, datetime, timedelta, timezone

from app.models.document import Document
from app.models.fiscal_check import FiscalListCheck
from app.services.validity_service import (
    check_csf_current_month,
    check_document_expiration,
    check_fiscal_staleness,
    get_expired_documents,
    needs_update,
)


class TestCheckDocumentExpiration:
    def test_expired(self):
        doc = Document(fecha_vencimiento=date.today() - timedelta(days=1))
        assert check_document_expiration(doc) is True

    def test_not_expired(self):
        doc = Document(fecha_vencimiento=date.today() + timedelta(days=30))
        assert check_document_expiration(doc) is False

    def test_no_date(self):
        doc = Document()
        assert check_document_expiration(doc) is False


class TestCheckCsfCurrentMonth:
    def test_current_month_from_fecha_emision(self):
        doc = Document(document_type="constancia_situacion_fiscal",
                       fecha_emision=date.today(), extraction_status="completed",
                       extracted_data={"fecha_emision": date.today().isoformat()})
        assert check_csf_current_month([doc]) is True

    def test_old_month(self):
        old = date.today().replace(day=1) - timedelta(days=1)
        doc = Document(document_type="constancia_situacion_fiscal",
                       fecha_emision=old, extraction_status="completed",
                       extracted_data={})
        assert check_csf_current_month([doc]) is False

    def test_no_csf(self):
        assert check_csf_current_month([]) is False

    def test_from_extracted_data(self):
        doc = Document(document_type="constancia_situacion_fiscal",
                       extraction_status="completed",
                       extracted_data={"fecha_emision": date.today().isoformat()})
        assert check_csf_current_month([doc]) is True


class TestCheckFiscalStaleness:
    def test_recent(self):
        fc = FiscalListCheck(checked_at=datetime.now(timezone.utc))
        assert check_fiscal_staleness([fc]) is False

    def test_stale(self):
        fc = FiscalListCheck(checked_at=datetime.now(timezone.utc) - timedelta(days=100))
        assert check_fiscal_staleness([fc]) is True

    def test_empty(self):
        assert check_fiscal_staleness([]) is True


class TestGetExpiredDocuments:
    def test_returns_expired(self):
        docs = [
            Document(fecha_vencimiento=date.today() - timedelta(days=1)),
            Document(fecha_vencimiento=date.today() + timedelta(days=30)),
        ]
        expired = get_expired_documents(docs)
        assert len(expired) == 1

    def test_no_expired(self):
        docs = [Document(fecha_vencimiento=date.today() + timedelta(days=30))]
        assert len(get_expired_documents(docs)) == 0


class TestNeedsUpdate:
    def test_expired_doc(self):
        docs = [Document(fecha_vencimiento=date.today() - timedelta(days=1))]
        assert needs_update(docs, []) is True

    def test_no_csf(self):
        assert needs_update([], []) is True

    def test_stale_fiscal(self):
        fc = FiscalListCheck(checked_at=datetime.now(timezone.utc) - timedelta(days=100))
        assert needs_update([], [fc]) is True

    def test_all_good(self):
        doc = Document(document_type="constancia_situacion_fiscal",
                       fecha_emision=date.today(), extraction_status="completed",
                       extracted_data={"fecha_emision": date.today().isoformat()})
        fc = FiscalListCheck(checked_at=datetime.now(timezone.utc))
        assert needs_update([doc], [fc]) is False
