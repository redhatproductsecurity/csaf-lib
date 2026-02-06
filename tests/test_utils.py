"""Tests for utility functions."""

from datetime import datetime, timedelta, timezone

import pytest

from csaf_lib.utils import format_datetime


class TestUtils:
    """Tests for utility functions."""

    @pytest.mark.parametrize(
        "dt,expected",
        [
            (datetime(2025, 12, 31, 23, 59, 59, 0, timezone.utc), "2025-12-31T23:59:59+00:00"),
            (datetime(2000, 1, 1, 0, 0, 0, 500000, timezone.utc), "2000-01-01T00:00:00+00:00"),
            (datetime(2025, 6, 15, 14, 22, 33, 777777, timezone.utc), "2025-06-15T14:22:33+00:00"),
            (
                datetime(2023, 3, 15, 9, 45, 12, 123, timezone(timedelta(hours=2))),
                "2023-03-15T09:45:12+02:00",
            ),
        ],
    )
    def test_format_datetime_various_cases(self, dt, expected):
        """Test format_datetime with various datetime values."""
        assert format_datetime(dt) == expected

    @pytest.mark.parametrize(
        "tz_offset,expected_dt",
        [
            (timezone.utc, "2025-01-01T12:30:45+00:00"),
            (timezone(timedelta(hours=-5)), "2025-01-01T12:30:45-05:00"),
            (timezone(timedelta(hours=3)), "2025-01-01T12:30:45+03:00"),
            (timezone(timedelta(hours=-8, minutes=-30)), "2025-01-01T12:30:45-08:30"),
        ],
    )
    def test_format_datetime_preserves_timezone(self, tz_offset, expected_dt):
        """Test timezone information is preserved for various timezones."""
        dt = datetime(2025, 1, 1, 12, 30, 45, 999999, tz_offset)
        result = format_datetime(dt)
        assert result == expected_dt
