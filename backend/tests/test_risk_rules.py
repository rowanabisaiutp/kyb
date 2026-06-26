from app.services.risk_rules import (
    ART_69B_SITUATION_RULES,
    DOC_EXPIRED_POINTS,
    DOC_MISSING_RULES,
    FISCAL_RULES,
    RECON_RULES,
    SUGGESTED_ACTIONS,
)


class TestFiscalRules:
    def test_has_7_rules(self):
        assert len(FISCAL_RULES) == 7

    def test_all_tuples_have_3_elements(self):
        for key, rule in FISCAL_RULES.items():
            assert len(rule) == 3, f"{key} should have (points, blocking, desc)"

    def test_blocking_rules_exist(self):
        blocking = {k for k, (_, b, _) in FISCAL_RULES.items() if b}
        assert "art_69_firmes" in blocking
        assert "art_69_no_localizados" in blocking
        assert "art_69_csd_sin_efectos" in blocking

    def test_points_are_positive(self):
        for key, (points, _, _) in FISCAL_RULES.items():
            assert points > 0, f"{key} should have positive points"


class TestArt69bSituationRules:
    def test_has_4_situations(self):
        assert len(ART_69B_SITUATION_RULES) == 4

    def test_definitivo_is_blocking(self):
        _, points, blocking, _ = ART_69B_SITUATION_RULES["Definitivo"]
        assert points == 50
        assert blocking is True

    def test_desvirtuado_is_low_risk(self):
        _, points, blocking, _ = ART_69B_SITUATION_RULES["Desvirtuado"]
        assert points == 5
        assert blocking is False

    def test_sentencia_favorable_is_zero(self):
        _, points, blocking, _ = ART_69B_SITUATION_RULES["Sentencia Favorable"]
        assert points == 0
        assert blocking is False


class TestDocMissingRules:
    def test_has_5_required_docs(self):
        assert len(DOC_MISSING_RULES) == 5

    def test_csf_has_highest_points(self):
        _, points, _ = DOC_MISSING_RULES["constancia_situacion_fiscal"]
        assert points == 20

    def test_all_have_code_and_description(self):
        for key, (code, points, desc) in DOC_MISSING_RULES.items():
            assert code.startswith("DOC_MISSING_"), f"{key} code should start with DOC_MISSING_"
            assert points > 0
            assert len(desc) > 0


class TestDocExpiredPoints:
    def test_comprobante_and_id_are_20(self):
        assert DOC_EXPIRED_POINTS["comprobante_domicilio"] == 20
        assert DOC_EXPIRED_POINTS["identificacion_representante"] == 20

    def test_only_2_entries(self):
        assert len(DOC_EXPIRED_POINTS) == 2


class TestReconRules:
    def test_has_6_fields(self):
        assert len(RECON_RULES) == 6

    def test_rfc_is_blocking(self):
        code, points, blocking, _ = RECON_RULES["rfc"]
        assert blocking is True
        assert points == 35

    def test_razon_social_not_blocking(self):
        _, _, blocking, _ = RECON_RULES["razon_social"]
        assert blocking is False

    def test_all_have_code_prefix(self):
        for key, (code, _, _, _) in RECON_RULES.items():
            assert code.startswith("RECON_"), f"{key} code should start with RECON_"


class TestSuggestedActions:
    def test_has_entries(self):
        assert len(SUGGESTED_ACTIONS) >= 20

    def test_all_values_are_spanish_strings(self):
        for code, action in SUGGESTED_ACTIONS.items():
            assert isinstance(action, str)
            assert len(action) > 5, f"{code} action too short"

    def test_critical_actions_marked(self):
        assert SUGGESTED_ACTIONS["FISCAL_69B_DEFINITIVO"].startswith("CRITICO")
        assert SUGGESTED_ACTIONS["RECON_RFC_MISMATCH"].startswith("CRITICO")

    def test_covers_all_doc_missing_codes(self):
        for _, (code, _, _) in DOC_MISSING_RULES.items():
            assert code in SUGGESTED_ACTIONS, f"Missing action for {code}"

    def test_covers_all_recon_codes(self):
        for _, (code, _, _, _) in RECON_RULES.items():
            assert code in SUGGESTED_ACTIONS, f"Missing action for {code}"
