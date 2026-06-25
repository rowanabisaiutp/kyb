from app.utils.rfc_validator import is_valid_rfc, normalize_rfc


class TestIsValidRfc:
    def test_valid_moral(self):
        assert is_valid_rfc("AAA010101AAA") is True

    def test_valid_fisica(self):
        assert is_valid_rfc("AAAA010101BB1") is True

    def test_lowercase(self):
        assert is_valid_rfc("aaa010101aaa") is True

    def test_too_short(self):
        assert is_valid_rfc("AA010101") is False

    def test_invalid_chars(self):
        assert is_valid_rfc("123456789012") is False

    def test_empty(self):
        assert is_valid_rfc("") is False

    def test_with_ampersand(self):
        assert is_valid_rfc("&HI0102165P2") is True


class TestNormalizeRfc:
    def test_uppercase(self):
        assert normalize_rfc("abc010101aa1") == "ABC010101AA1"

    def test_strip(self):
        assert normalize_rfc("  ABC010101AA1  ") == "ABC010101AA1"
