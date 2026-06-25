from app.utils.text_normalization import (
    business_names_match,
    normalize_address,
    normalize_business_name,
    normalize_text,
    similarity_ratio,
    texts_match,
)


class TestNormalizeText:
    def test_uppercase_and_strip(self):
        assert normalize_text("  hello world  ") == "HELLO WORLD"

    def test_accents_removed(self):
        assert normalize_text("compañía") == "COMPANIA"

    def test_none_returns_empty(self):
        assert normalize_text(None) == ""

    def test_multiple_spaces(self):
        assert normalize_text("a    b") == "A B"


class TestNormalizeBusinessName:
    def test_sa_de_cv_variations(self):
        assert normalize_business_name("Empresa S.A. de C.V.") == "EMPRESA SA DE CV"
        assert normalize_business_name("Empresa SA DE CV") == "EMPRESA SA DE CV"
        assert normalize_business_name("Empresa S.A. DE C.V.") == "EMPRESA SA DE CV"

    def test_sociedad_anonima_full(self):
        result = normalize_business_name("Empresa Sociedad Anonima de Capital Variable")
        assert "SA DE CV" in result

    def test_none(self):
        assert normalize_business_name(None) == ""

    def test_punctuation_removed(self):
        result = normalize_business_name("Empresa (Test), S.A.")
        assert "(" not in result
        assert ")" not in result


class TestNormalizeAddress:
    def test_abbreviations(self):
        result = normalize_address("Calle Reforma Numero 100, Colonia Centro")
        assert "CALLE" not in result
        assert "NUM" in result
        assert "COL" in result

    def test_none(self):
        assert normalize_address(None) == ""


class TestSimilarityRatio:
    def test_identical(self):
        assert similarity_ratio("A B C", "A B C") == 1.0

    def test_empty(self):
        assert similarity_ratio("", "") == 0.0

    def test_partial_match(self):
        ratio = similarity_ratio("A B C D", "A B E F")
        assert 0.0 < ratio < 1.0


class TestTextsMatch:
    def test_exact_match(self):
        assert texts_match("Hello", "hello") is True

    def test_no_match(self):
        assert texts_match("Apple", "Orange") is False

    def test_none_values(self):
        assert texts_match(None, None) is True
        assert texts_match("test", None) is False


class TestBusinessNamesMatch:
    def test_same_name_different_suffix(self):
        assert business_names_match(
            "EMPRESA TEST S.A. DE C.V.",
            "EMPRESA TEST SA DE CV"
        ) is True

    def test_different_names(self):
        assert business_names_match(
            "EMPRESA ALPHA SA DE CV",
            "EMPRESA BETA SA DE CV"
        ) is False

    def test_accents(self):
        assert business_names_match(
            "COMPAÑIA TEST SA",
            "COMPANIA TEST SA"
        ) is True
