from app.models.document import Document
from app.models.entity import LegalEntity, LegalRepresentative, Shareholder
from app.models.fiscal_check import FiscalListCheck
from app.models.reconciliation import ReconciliationResult
from app.services.risk_engine import RiskFactor, calculate_risk, classify


class TestClassify:
    def test_safe(self):
        assert classify(0, False) == "safe"
        assert classify(19, False) == "safe"

    def test_review_required(self):
        assert classify(20, False) == "review_required"
        assert classify(49, False) == "review_required"

    def test_high_risk_by_score(self):
        assert classify(50, False) == "high_risk"
        assert classify(100, False) == "high_risk"

    def test_high_risk_by_blocking(self):
        assert classify(0, True) == "high_risk"
        assert classify(10, True) == "high_risk"


def _make_entity(rfc="TEST010101000", reps=True, shareholders=True):
    entity = LegalEntity(rfc=rfc, razon_social="Test SA de CV")
    if reps:
        entity.representatives = [
            LegalRepresentative(nombre_completo="Juan Perez", entity_id=entity.id)
        ]
    else:
        entity.representatives = []
    if shareholders:
        entity.shareholders = [
            Shareholder(nombre_completo="Ana", tipo="socio", entity_id=entity.id)
        ]
    else:
        entity.shareholders = []
    return entity


def _make_docs(types=None):
    if types is None:
        types = [
            "acta_constitutiva",
            "identificacion_representante",
            "comprobante_domicilio",
            "constancia_situacion_fiscal",
            "manifestacion_protesta",
        ]
    return [
        Document(document_type=t, file_name=f"{t}.pdf", extraction_status="completed")
        for t in types
    ]


def _make_clean_fiscal():
    from datetime import datetime, timezone

    checks = []
    for lt in [
        "art_69_cancelados",
        "art_69_exigibles",
        "art_69_firmes",
        "art_69_no_localizados",
        "art_69_sentencias",
        "art_69_csd_sin_efectos",
        "art_69b",
        "art_69b_bis",
        "art_49bis",
    ]:
        checks.append(
            FiscalListCheck(
                rfc_searched="TEST",
                list_type=lt,
                source_url="test",
                found=False,
                checked_at=datetime.now(timezone.utc),
            )
        )
    return checks


class TestCalculateRiskSafe:
    def test_complete_dossier_is_safe(self):
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        assert result.classification == "safe"
        assert result.blocks_approval is False
        assert result.total_score < 20

    def test_no_factors_blocking(self):
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        assert all(not f.blocking for f in result.factors)


class TestCalculateRiskDocuments:
    def test_missing_acta(self):
        docs = _make_docs(
            [
                "identificacion_representante",
                "comprobante_domicilio",
                "constancia_situacion_fiscal",
                "manifestacion_protesta",
            ]
        )
        result = calculate_risk(
            entity=_make_entity(),
            documents=docs,
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "DOC_MISSING_ACTA" in codes

    def test_missing_csf(self):
        docs = _make_docs(
            [
                "acta_constitutiva",
                "identificacion_representante",
                "comprobante_domicilio",
                "manifestacion_protesta",
            ]
        )
        result = calculate_risk(
            entity=_make_entity(),
            documents=docs,
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "DOC_MISSING_CSF" in codes

    def test_all_docs_missing(self):
        result = calculate_risk(
            entity=_make_entity(),
            documents=[],
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "DOC_MISSING_ACTA" in codes
        assert "DOC_MISSING_CSF" in codes
        assert "DOC_MISSING_COMPROBANTE" in codes
        assert "DOC_MISSING_ID_REP" in codes
        assert "DOC_MISSING_MANIFESTACION" in codes

    def test_expired_document(self):
        from datetime import date, timedelta

        doc = Document(
            document_type="comprobante_domicilio",
            file_name="comp.pdf",
            extraction_status="completed",
            fecha_vencimiento=date.today() - timedelta(days=30),
        )
        docs = _make_docs(
            [
                "acta_constitutiva",
                "identificacion_representante",
                "constancia_situacion_fiscal",
                "manifestacion_protesta",
            ]
        )
        docs.append(doc)
        result = calculate_risk(
            entity=_make_entity(),
            documents=docs,
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "DOC_EXPIRED" in codes


class TestCalculateRiskFiscal:
    def test_found_in_firmes(self):
        checks = _make_clean_fiscal()
        for c in checks:
            if c.list_type == "art_69_firmes":
                c.found = True
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=checks,
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "FISCAL_69_FIRMES" in codes
        blocking = [f for f in result.factors if f.code == "FISCAL_69_FIRMES"]
        assert blocking[0].blocking is True
        assert result.classification == "high_risk"

    def test_found_in_69b_definitivo(self):
        checks = _make_clean_fiscal()
        for c in checks:
            if c.list_type == "art_69b":
                c.found = True
                c.result_detail = [{"Situacion del contribuyente": "Definitivo"}]
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=checks,
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "FISCAL_69B_DEFINITIVO" in codes
        assert result.blocks_approval is True

    def test_found_in_69b_desvirtuado(self):
        checks = _make_clean_fiscal()
        for c in checks:
            if c.list_type == "art_69b":
                c.found = True
                c.result_detail = [{"Situacion del contribuyente": "Desvirtuado"}]
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=checks,
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "FISCAL_69B_DESVIRTUADO" in codes
        desv = [f for f in result.factors if f.code == "FISCAL_69B_DESVIRTUADO"]
        assert desv[0].points == 5
        assert desv[0].blocking is False

    def test_never_checked(self):
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=[],
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "FISCAL_NEVER_CHECKED" in codes

    def test_found_in_49bis_with_69b(self):
        checks = _make_clean_fiscal()
        for c in checks:
            if c.list_type in ("art_69b", "art_49bis"):
                c.found = True
                c.result_detail = [{"Situacion del contribuyente": "Definitivo"}]
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=checks,
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "FISCAL_69B_DEFINITIVO" in codes
        assert "FISCAL_49BIS" in codes
        f49 = [f for f in result.factors if f.code == "FISCAL_49BIS"]
        assert f49[0].points == 0

    def test_found_in_49bis_without_69b(self):
        checks = _make_clean_fiscal()
        for c in checks:
            if c.list_type == "art_49bis":
                c.found = True
                c.result_detail = [{"Situacion del contribuyente": "Definitivo"}]
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=checks,
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "FISCAL_49BIS" in codes
        f49 = [f for f in result.factors if f.code == "FISCAL_49BIS"]
        assert f49[0].points == 45
        assert f49[0].blocking is True

    def test_found_in_no_localizados(self):
        checks = _make_clean_fiscal()
        for c in checks:
            if c.list_type == "art_69_no_localizados":
                c.found = True
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=checks,
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "FISCAL_69_NO_LOCALIZADOS" in codes
        assert result.blocks_approval is True


class TestCalculateRiskReconciliation:
    def test_rfc_mismatch_is_critical(self):
        recon = [
            ReconciliationResult(
                field_name="rfc",
                source_a="formulario",
                source_b="csf",
                value_a="AAA",
                value_b="BBB",
                match=False,
                severity="critical",
            )
        ]
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=recon,
        )
        codes = [f.code for f in result.factors]
        assert "RECON_RFC_MISMATCH" in codes
        rfc_factor = [f for f in result.factors if f.code == "RECON_RFC_MISMATCH"]
        assert rfc_factor[0].blocking is True
        assert result.classification == "high_risk"

    def test_razon_social_mismatch(self):
        recon = [
            ReconciliationResult(
                field_name="razon_social",
                source_a="formulario",
                source_b="csf",
                value_a="Test SA",
                value_b="Otra SA",
                match=False,
                severity="warning",
            )
        ]
        result = calculate_risk(
            entity=_make_entity(),
            documents=_make_docs(),
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=recon,
        )
        codes = [f.code for f in result.factors]
        assert "RECON_RAZON_SOCIAL_MISMATCH" in codes


class TestCalculateRiskCompleteness:
    def test_no_rep_legal(self):
        result = calculate_risk(
            entity=_make_entity(reps=False),
            documents=_make_docs(),
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "COMP_NO_REP_LEGAL" in codes

    def test_no_shareholders(self):
        result = calculate_risk(
            entity=_make_entity(shareholders=False),
            documents=_make_docs(),
            fiscal_checks=_make_clean_fiscal(),
            reconciliation_results=[],
        )
        codes = [f.code for f in result.factors]
        assert "COMP_NO_SHAREHOLDERS" in codes


class TestSuggestedActions:
    def test_actions_generated(self):
        result = calculate_risk(
            entity=_make_entity(reps=False, shareholders=False),
            documents=[],
            fiscal_checks=[],
            reconciliation_results=[],
        )
        assert len(result.suggested_actions) > 0

    def test_no_duplicate_actions(self):
        result = calculate_risk(
            entity=_make_entity(reps=False, shareholders=False),
            documents=[],
            fiscal_checks=[],
            reconciliation_results=[],
        )
        assert len(result.suggested_actions) == len(set(result.suggested_actions))
