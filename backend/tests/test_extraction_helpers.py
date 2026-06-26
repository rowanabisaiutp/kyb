from app.services.extraction_service import _extract_pdf_text, _get_prompt


class TestGetPrompt:
    def test_known_type(self):
        prompt = _get_prompt("constancia_situacion_fiscal")
        assert "Constancia de Situacion Fiscal" in prompt
        assert "JSON" in prompt

    def test_acta_type(self):
        prompt = _get_prompt("acta_constitutiva")
        assert "Acta Constitutiva" in prompt

    def test_unknown_type_returns_default(self):
        prompt = _get_prompt("tipo_inventado")
        assert "datos relevantes" in prompt

    def test_all_known_types_have_json(self):
        known_types = [
            "constancia_situacion_fiscal",
            "acta_constitutiva",
            "identificacion_representante",
            "comprobante_domicilio",
            "poder_representacion",
            "manifestacion_protesta",
        ]
        for dt in known_types:
            assert "JSON" in _get_prompt(dt), f"{dt} prompt should mention JSON"


class TestExtractPdfText:
    def test_non_pdf_returns_none(self):
        assert _extract_pdf_text(b"image data", "image/jpeg") is None

    def test_invalid_pdf_returns_none(self):
        result = _extract_pdf_text(b"not a real pdf", "application/pdf")
        assert result is None or result == ""
