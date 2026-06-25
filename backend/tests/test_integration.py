"""Integration tests: todos los flujos E2E en una sola clase para compartir el event loop."""

import uuid
from datetime import datetime, timezone

import pytest

import app.database as _db

def _get_session():
    return _db.async_session()

async_session = lambda: _db.async_session()
from app.models.document import Document
from app.services.fiscal_service import set_loaded_lists


def _clean_fiscal():
    set_loaded_lists({
        "art_69_cancelados": {}, "art_69_exigibles": {}, "art_69_firmes": {},
        "art_69_no_localizados": {}, "art_69_sentencias": {},
        "art_69_csd_sin_efectos": {}, "art_69b": {}, "art_69b_bis": {},
    })


async def _new_entity(client, rfc=None):
    rfc = rfc or f"TST{uuid.uuid4().hex[:6].upper()}010100"
    r = await client.post("/api/v1/entities", json={
        "rfc": rfc, "razon_social": "Test SA de CV",
        "domicilio_fiscal": "Av Reforma 222, CDMX",
        "representatives": [{"nombre_completo": "Juan Test", "cargo": "Director"}],
        "shareholders": [{"nombre_completo": "Ana Test", "tipo": "socio"}],
    })
    assert r.status_code == 201, f"Entity creation failed: {r.text}"
    return r.json()


async def _new_dossier(client):
    entity = await _new_entity(client)
    r = await client.post("/api/v1/dossiers", json={"entity_id": entity["id"]})
    assert r.status_code == 201
    return entity, r.json()


@pytest.mark.asyncio(loop_scope="session")
class TestIntegration:
    # --- Entities ---
    async def test_create_entity(self, client):
        r = await client.post("/api/v1/entities", json={
            "rfc": f"E{uuid.uuid4().hex[:11].upper()}", "razon_social": "Create SA",
        })
        assert r.status_code == 201

    async def test_duplicate_rfc(self, client):
        rfc = f"D{uuid.uuid4().hex[:11].upper()}"
        await client.post("/api/v1/entities", json={"rfc": rfc, "razon_social": "Dup1"})
        r = await client.post("/api/v1/entities", json={"rfc": rfc, "razon_social": "Dup2"})
        assert r.status_code == 409

    async def test_get_entity(self, client):
        e = await _new_entity(client)
        r = await client.get(f"/api/v1/entities/{e['id']}")
        assert r.status_code == 200
        assert r.json()["rfc"] == e["rfc"]

    async def test_update_entity(self, client):
        e = await _new_entity(client)
        r = await client.put(f"/api/v1/entities/{e['id']}", json={"razon_social": "Updated SA"})
        assert r.status_code == 200
        assert r.json()["razon_social"] == "Updated SA"

    async def test_list_entities(self, client):
        r = await client.get("/api/v1/entities")
        assert r.status_code == 200

    async def test_add_representative(self, client):
        e = await _new_entity(client)
        r = await client.post(f"/api/v1/entities/{e['id']}/representatives",
                               json={"nombre_completo": "Nuevo Rep", "cargo": "Gerente"})
        assert r.status_code == 201

    async def test_add_shareholder(self, client):
        e = await _new_entity(client)
        r = await client.post(f"/api/v1/entities/{e['id']}/shareholders",
                               json={"nombre_completo": "Nuevo Socio", "tipo": "socio"})
        assert r.status_code == 201

    # --- Dossiers ---
    async def test_create_dossier(self, client):
        _, d = await _new_dossier(client)
        assert d["status"] == "draft"

    async def test_dossier_stats(self, client):
        r = await client.get("/api/v1/dossiers/stats")
        assert r.status_code == 200

    async def test_status_transitions(self, client):
        _, d = await _new_dossier(client)
        did = d["id"]
        r = await client.patch(f"/api/v1/dossiers/{did}/status", json={"status": "in_review"})
        assert r.status_code == 200
        r = await client.patch(f"/api/v1/dossiers/{did}/status", json={"status": "needs_update"})
        assert r.status_code == 200
        r = await client.patch(f"/api/v1/dossiers/{did}/status", json={"status": "in_review"})
        assert r.status_code == 200
        r = await client.patch(f"/api/v1/dossiers/{did}/status", json={"status": "rejected"})
        assert r.status_code == 200
        r = await client.patch(f"/api/v1/dossiers/{did}/status", json={"status": "in_review"})
        assert r.status_code == 200
        r = await client.patch(f"/api/v1/dossiers/{did}/status",
                               json={"status": "approved", "approved_by": "Admin"})
        assert r.status_code == 200
        r = await client.patch(f"/api/v1/dossiers/{did}/status", json={"status": "needs_update"})
        assert r.status_code == 200

    async def test_invalid_transitions(self, client):
        _, d = await _new_dossier(client)
        r = await client.patch(f"/api/v1/dossiers/{d['id']}/status", json={"status": "approved"})
        assert r.status_code == 400

    # --- Documents ---
    async def test_upload_document(self, client):
        _, d = await _new_dossier(client)
        r = await client.post(f"/api/v1/dossiers/{d['id']}/documents",
                               files={"file": ("test.pdf", b"%PDF-1.4 fake", "application/pdf")},
                               data={"document_type": "acta_constitutiva"})
        assert r.status_code == 201

    async def test_upload_invalid_type(self, client):
        _, d = await _new_dossier(client)
        r = await client.post(f"/api/v1/dossiers/{d['id']}/documents",
                               files={"file": ("test.js", b"alert(1)", "text/javascript")},
                               data={"document_type": "otro"})
        assert r.status_code == 400

    async def test_document_checklist(self, client):
        _, d = await _new_dossier(client)
        r = await client.get(f"/api/v1/dossiers/{d['id']}/documents/checklist")
        assert r.json()["total_present"] == 0
        assert len(r.json()["missing"]) == 5

    async def test_delete_document(self, client):
        _, d = await _new_dossier(client)
        r = await client.post(f"/api/v1/dossiers/{d['id']}/documents",
                               files={"file": ("del.pdf", b"%PDF", "application/pdf")},
                               data={"document_type": "otro"})
        doc_id = r.json()["id"]
        r = await client.delete(f"/api/v1/documents/{doc_id}")
        assert r.status_code == 204

    # --- Fiscal ---
    async def test_fiscal_check_clean(self, client):
        _, d = await _new_dossier(client)
        _clean_fiscal()
        r = await client.post(f"/api/v1/dossiers/{d['id']}/fiscal-check")
        assert r.json()["clean"] is True

    async def test_fiscal_check_match(self, client):
        e, d = await _new_dossier(client)
        set_loaded_lists({
            "art_69_firmes": {e["rfc"]: [{"RFC": e["rfc"]}]},
            "art_69_cancelados": {}, "art_69_exigibles": {},
            "art_69_no_localizados": {}, "art_69_sentencias": {},
            "art_69_csd_sin_efectos": {}, "art_69b": {}, "art_69b_bis": {},
        })
        r = await client.post(f"/api/v1/dossiers/{d['id']}/fiscal-check")
        assert r.json()["matches_found"] == 1
        assert r.json()["clean"] is False

    async def test_fiscal_multiple_matches(self, client):
        e, d = await _new_dossier(client)
        set_loaded_lists({
            "art_69_cancelados": {e["rfc"]: [{"RFC": e["rfc"]}]},
            "art_69_exigibles": {e["rfc"]: [{"RFC": e["rfc"]}]},
            "art_69_firmes": {e["rfc"]: [{"RFC": e["rfc"]}]},
            "art_69_no_localizados": {}, "art_69_sentencias": {},
            "art_69_csd_sin_efectos": {}, "art_69b": {}, "art_69b_bis": {},
        })
        r = await client.post(f"/api/v1/dossiers/{d['id']}/fiscal-check")
        assert r.json()["matches_found"] == 3

    async def test_fiscal_status(self, client):
        r = await client.get("/api/v1/fiscal-lists/status")
        assert r.status_code == 200

    # --- Reconciliation ---
    async def test_reconciliation_mismatch(self, client):
        e, d = await _new_dossier(client)
        async with async_session() as db:
            db.add(Document(dossier_id=uuid.UUID(d["id"]), document_type="constancia_situacion_fiscal",
                            file_name="csf.pdf", extraction_status="completed",
                            extracted_data={"rfc": e["rfc"], "razon_social": "DIFERENTE SA"}))
            await db.commit()
        r = await client.post(f"/api/v1/dossiers/{d['id']}/reconciliation")
        assert r.json()["discrepancies"] > 0

    async def test_reconciliation_rfc_critical(self, client):
        _, d = await _new_dossier(client)
        async with async_session() as db:
            db.add(Document(dossier_id=uuid.UUID(d["id"]), document_type="constancia_situacion_fiscal",
                            file_name="csf.pdf", extraction_status="completed",
                            extracted_data={"rfc": "AAA111111111", "razon_social": "T"}))
            db.add(Document(dossier_id=uuid.UUID(d["id"]), document_type="acta_constitutiva",
                            file_name="acta.pdf", extraction_status="completed",
                            extracted_data={"rfc": "BBB222222222", "razon_social": "T"}))
            await db.commit()
        r = await client.post(f"/api/v1/dossiers/{d['id']}/reconciliation")
        assert r.json()["has_critical"] is True

    # --- Risk ---
    async def test_risk_assessment(self, client):
        _, d = await _new_dossier(client)
        r = await client.post(f"/api/v1/dossiers/{d['id']}/risk-assessment")
        assert r.status_code == 200
        assert "total_score" in r.json()
        assert "factors" in r.json()

    async def test_risk_high_risk_blocks(self, client):
        e, d = await _new_dossier(client)
        set_loaded_lists({
            "art_69_cancelados": {}, "art_69_exigibles": {}, "art_69_firmes": {},
            "art_69_no_localizados": {}, "art_69_sentencias": {}, "art_69_csd_sin_efectos": {},
            "art_69b": {e["rfc"]: [{"RFC": e["rfc"], "Situacion del contribuyente": "Definitivo"}]},
            "art_69b_bis": {},
        })
        await client.post(f"/api/v1/dossiers/{d['id']}/fiscal-check")
        r = await client.post(f"/api/v1/dossiers/{d['id']}/risk-assessment")
        assert r.json()["classification"] == "high_risk"
        assert r.json()["blocks_approval"] is True

    async def test_risk_history(self, client):
        _, d = await _new_dossier(client)
        await client.post(f"/api/v1/dossiers/{d['id']}/risk-assessment")
        await client.post(f"/api/v1/dossiers/{d['id']}/risk-assessment")
        r = await client.get(f"/api/v1/dossiers/{d['id']}/risk-assessments")
        assert len(r.json()) >= 2

    async def test_risk_latest(self, client):
        _, d = await _new_dossier(client)
        await client.post(f"/api/v1/dossiers/{d['id']}/risk-assessment")
        r = await client.get(f"/api/v1/dossiers/{d['id']}/risk-assessment/latest")
        assert r.json() is not None

    # --- Approval flow ---
    async def test_approve_safe(self, client):
        _, d = await _new_dossier(client)
        await client.patch(f"/api/v1/dossiers/{d['id']}/status", json={"status": "in_review"})
        r = await client.patch(f"/api/v1/dossiers/{d['id']}/status",
                               json={"status": "approved", "approved_by": "Admin"})
        assert r.status_code == 200
        assert r.json()["status"] == "approved"

    async def test_approve_high_risk_blocked(self, client):
        e, d = await _new_dossier(client)
        set_loaded_lists({
            "art_69_firmes": {e["rfc"]: [{"RFC": e["rfc"]}]},
            "art_69_cancelados": {}, "art_69_exigibles": {},
            "art_69_no_localizados": {}, "art_69_sentencias": {},
            "art_69_csd_sin_efectos": {}, "art_69b": {}, "art_69b_bis": {},
        })
        await client.post(f"/api/v1/dossiers/{d['id']}/fiscal-check")
        await client.post(f"/api/v1/dossiers/{d['id']}/risk-assessment")
        await client.patch(f"/api/v1/dossiers/{d['id']}/status", json={"status": "in_review"})
        r = await client.patch(f"/api/v1/dossiers/{d['id']}/status",
                               json={"status": "approved", "approved_by": "Admin"})
        assert r.status_code == 400

    async def test_reject(self, client):
        _, d = await _new_dossier(client)
        await client.patch(f"/api/v1/dossiers/{d['id']}/status", json={"status": "in_review"})
        r = await client.patch(f"/api/v1/dossiers/{d['id']}/status", json={"status": "rejected"})
        assert r.json()["status"] == "rejected"

    # --- Audit ---
    async def test_audit_log(self, client):
        _, d = await _new_dossier(client)
        r = await client.get(f"/api/v1/dossiers/{d['id']}/audit-log")
        assert r.status_code == 200
        actions = [e["action"] for e in r.json()]
        assert "dossier.created" in actions

    async def test_global_audit_log(self, client):
        r = await client.get("/api/v1/audit-log")
        assert r.status_code == 200

    # --- Full safe flow ---
    async def test_complete_safe_flow(self, client):
        e, d = await _new_dossier(client)
        did = d["id"]
        async with async_session() as db:
            for dt in ["acta_constitutiva", "identificacion_representante", "comprobante_domicilio",
                       "constancia_situacion_fiscal", "manifestacion_protesta"]:
                db.add(Document(dossier_id=uuid.UUID(did), document_type=dt, file_name=f"{dt}.pdf",
                                extraction_status="completed",
                                extracted_data={"rfc": e["rfc"], "razon_social": "TEST SA DE CV",
                                                "fecha_emision": datetime.now(timezone.utc).strftime("%Y-%m-%d")}))
            await db.commit()

        r = await client.get(f"/api/v1/dossiers/{did}/documents/checklist")
        assert r.json()["total_present"] == 5

        _clean_fiscal()
        r = await client.post(f"/api/v1/dossiers/{did}/fiscal-check")
        assert r.json()["clean"] is True

        r = await client.post(f"/api/v1/dossiers/{did}/reconciliation")
        assert r.json()["has_critical"] is False

        r = await client.post(f"/api/v1/dossiers/{did}/risk-assessment")
        assert r.json()["classification"] == "safe"

        await client.patch(f"/api/v1/dossiers/{did}/status", json={"status": "in_review"})
        r = await client.post(f"/api/v1/dossiers/{did}/risk-assessment")
        r = await client.patch(f"/api/v1/dossiers/{did}/status",
                               json={"status": "approved", "approved_by": "Compliance"})
        assert r.json()["status"] == "approved"

        r = await client.get(f"/api/v1/dossiers/{did}/audit-log")
        actions = [e["action"] for e in r.json()]
        assert "dossier.created" in actions
        assert "fiscal.checked" in actions
        assert "risk.calculated" in actions
