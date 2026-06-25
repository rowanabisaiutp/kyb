from datetime import date, timedelta

from app.utils.date_utils import is_current_month, is_expired, is_older_than_months, safe_parse_date


class TestIsCurrentMonth:
    def test_today(self):
        assert is_current_month(date.today()) is True

    def test_last_month(self):
        last = date.today().replace(day=1) - timedelta(days=1)
        assert is_current_month(last) is False

    def test_none(self):
        assert is_current_month(None) is False


class TestIsExpired:
    def test_past_date(self):
        assert is_expired(date.today() - timedelta(days=1)) is True

    def test_future_date(self):
        assert is_expired(date.today() + timedelta(days=30)) is False

    def test_today(self):
        assert is_expired(date.today()) is False

    def test_none(self):
        assert is_expired(None) is False


class TestIsOlderThanMonths:
    def test_old_date(self):
        assert is_older_than_months(date.today() - timedelta(days=100), 3) is True

    def test_recent_date(self):
        assert is_older_than_months(date.today() - timedelta(days=10), 3) is False

    def test_none(self):
        assert is_older_than_months(None, 3) is True


class TestSafeParseDate:
    def test_iso_format(self):
        assert safe_parse_date("2026-06-15") == date(2026, 6, 15)

    def test_mexican_format(self):
        assert safe_parse_date("15/06/2026") == date(2026, 6, 15)

    def test_dash_format(self):
        assert safe_parse_date("15-06-2026") == date(2026, 6, 15)

    def test_invalid(self):
        assert safe_parse_date("not a date") is None

    def test_none(self):
        assert safe_parse_date(None) is None

    def test_empty(self):
        assert safe_parse_date("") is None
