import uuid

from app.models.document import Document
from app.models.entity import LegalEntity, LegalRepresentative
from app.services.reconciliation_service import (
    _collect_field_sources,
    _compare_pairs,
    _compare_values,
    _extract_value,
    _get_entity_value,
)


class TestExtractValue:
    def test_extracts_first_matching_key(self):
        data = {"rfc": "AAA111", "other": "x"}
        assert _extract_value(data, ["rfc"]) == "AAA111"

    def test_returns_none_for_missing_key(self):
        assert _extract_value({"a": "1"}, ["b"]) is None

    def test_returns_none_for_empty_data(self):
        assert _extract_value(None, ["rfc"]) is None

    def test_strips_whitespace(self):
        assert _extract_value({"rfc": "  AAA  "}, ["rfc"]) == "AAA"

    def test_skips_empty_values(self):
        data = {"rfc": "", "rfc2": "BBB"}
        assert _extract_value(data, ["rfc", "rfc2"]) == "BBB"


class TestCompareValues:
    def test_rfc_exact_match(self):
        assert _compare_values("rfc", "AAA111111111", "aaa111111111") is True

    def test_rfc_mismatch(self):
        assert _compare_values("rfc", "AAA111111111", "BBB222222222") is False

    def test_none_values_equal(self):
        assert _compare_values("rfc", None, None) is True

    def test_one_none_is_false(self):
        assert _compare_values("rfc", "AAA", None) is False

    def test_date_comparison(self):
        assert _compare_values("fecha_emision", "2026-01-15", "15/01/2026") is True


class TestGetEntityValue:
    def test_rfc(self):
        entity = LegalEntity(rfc="TEST123", razon_social="Test SA")
        assert _get_entity_value(entity, "rfc") == "TEST123"

    def test_razon_social(self):
        entity = LegalEntity(rfc="TEST123", razon_social="Test SA")
        assert _get_entity_value(entity, "razon_social") == "Test SA"

    def test_domicilio(self):
        entity = LegalEntity(rfc="T", razon_social="T", domicilio_fiscal="Reforma 222")
        assert _get_entity_value(entity, "domicilio") == "Reforma 222"

    def test_representante_legal(self):
        entity = LegalEntity(rfc="T", razon_social="T")
        entity.representatives = [LegalRepresentative(nombre_completo="Juan Perez")]
        assert _get_entity_value(entity, "representante_legal") == "Juan Perez"

    def test_unknown_field(self):
        entity = LegalEntity(rfc="T", razon_social="T")
        assert _get_entity_value(entity, "unknown_field") is None


class TestCollectFieldSources:
    def test_collects_entity_and_doc_values(self):
        entity = LegalEntity(rfc="AAA111", razon_social="Test SA")
        doc = Document(
            document_type="constancia_situacion_fiscal",
            extraction_status="completed",
            extracted_data={"rfc": "AAA111"},
        )
        sources = {"constancia_situacion_fiscal": ["rfc"]}
        result = _collect_field_sources("rfc", sources, entity, {"constancia_situacion_fiscal": doc})
        assert len(result) == 2
        assert result[0] == ("formulario", "AAA111")
        assert result[1] == ("constancia_situacion_fiscal", "AAA111")

    def test_skips_missing_docs(self):
        entity = LegalEntity(rfc="AAA111", razon_social="Test SA")
        sources = {"constancia_situacion_fiscal": ["rfc"]}
        result = _collect_field_sources("rfc", sources, entity, {})
        assert len(result) == 1

    def test_skips_docs_without_extracted_data(self):
        entity = LegalEntity(rfc="AAA111", razon_social="Test SA")
        doc = Document(
            document_type="constancia_situacion_fiscal",
            extraction_status="completed",
            extracted_data=None,
        )
        sources = {"constancia_situacion_fiscal": ["rfc"]}
        result = _collect_field_sources("rfc", sources, entity, {"constancia_situacion_fiscal": doc})
        assert len(result) == 1


class TestComparePairs:
    def test_two_sources_one_pair(self):
        dossier_id = uuid.uuid4()
        sources = [("formulario", "AAA"), ("csf", "BBB")]
        results = _compare_pairs(dossier_id, "rfc", sources)
        assert len(results) == 1
        assert results[0].match is False
        assert results[0].severity == "critical"

    def test_three_sources_three_pairs(self):
        dossier_id = uuid.uuid4()
        sources = [("formulario", "AAA"), ("csf", "AAA"), ("acta", "AAA")]
        results = _compare_pairs(dossier_id, "rfc", sources)
        assert len(results) == 3
        assert all(r.match for r in results)

    def test_matching_has_no_severity(self):
        dossier_id = uuid.uuid4()
        sources = [("formulario", "AAA"), ("csf", "AAA")]
        results = _compare_pairs(dossier_id, "rfc", sources)
        assert results[0].severity is None

    def test_empty_sources_no_pairs(self):
        results = _compare_pairs(uuid.uuid4(), "rfc", [])
        assert len(results) == 0
