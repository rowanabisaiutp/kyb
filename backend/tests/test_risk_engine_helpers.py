from app.models.fiscal_check import FiscalListCheck
from app.services.risk_engine import _extract_69b_situation


class TestExtract69bSituation:
    def test_extracts_situacion(self):
        fc = FiscalListCheck(result_detail=[{"Situacion": "Definitivo"}])
        assert _extract_69b_situation(fc) == "Definitivo"

    def test_extracts_situacion_del_contribuyente(self):
        fc = FiscalListCheck(
            result_detail=[{"Situacion del contribuyente": "Presunto"}]
        )
        assert _extract_69b_situation(fc) == "Presunto"

    def test_extracts_uppercase_key(self):
        fc = FiscalListCheck(result_detail=[{"SITUACION": "Desvirtuado"}])
        assert _extract_69b_situation(fc) == "Desvirtuado"

    def test_returns_none_when_no_detail(self):
        fc = FiscalListCheck(result_detail=None)
        assert _extract_69b_situation(fc) is None

    def test_returns_none_when_empty_detail(self):
        fc = FiscalListCheck(result_detail=[])
        assert _extract_69b_situation(fc) is None

    def test_handles_dict_instead_of_list(self):
        fc = FiscalListCheck(result_detail={"Situacion": "Definitivo"})
        assert _extract_69b_situation(fc) == "Definitivo"

    def test_strips_whitespace(self):
        fc = FiscalListCheck(result_detail=[{"Situacion": "  Presunto  "}])
        assert _extract_69b_situation(fc) == "Presunto"

    def test_skips_non_dict_rows(self):
        fc = FiscalListCheck(result_detail=["not a dict", {"Situacion": "Definitivo"}])
        assert _extract_69b_situation(fc) == "Definitivo"
