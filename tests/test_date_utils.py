"""
Tests for date utilities module.
"""

from datetime import datetime

import pytz

from src.utils.date_utils import (
    format_datetime,
    format_friendly_date,
    get_lookback_time,
    get_timezone,
    is_market_open,
    now,
    parse_datetime,
)


def test_get_timezone():
    """Test timezone retrieval."""
    tz = get_timezone("Europe/Paris")
    assert isinstance(tz, pytz.tzinfo.BaseTzInfo)

    # Invalid timezone should return UTC
    tz_invalid = get_timezone("Invalid/Timezone")
    assert tz_invalid == pytz.UTC


def test_now():
    """Test current time retrieval."""
    current = now()
    assert isinstance(current, datetime)
    assert current.tzinfo is not None

    # With specific timezone
    current_paris = now("Europe/Paris")
    assert current_paris.tzinfo is not None


def test_format_datetime():
    """Test datetime formatting."""
    dt = datetime(2025, 11, 11, 10, 30, 0, tzinfo=pytz.UTC)
    formatted = format_datetime(dt, fmt="%Y-%m-%d")

    assert isinstance(formatted, str)
    assert "2025-11-11" in formatted


def test_parse_datetime():
    """Test datetime parsing."""
    dt_str = "2025-11-11 10:30:00"
    dt = parse_datetime(dt_str, fmt="%Y-%m-%d %H:%M:%S")

    assert isinstance(dt, datetime)
    assert dt.year == 2025
    assert dt.month == 11
    assert dt.day == 11
    assert dt.tzinfo is not None


def test_get_lookback_time():
    """Test lookback time calculation."""
    reference = datetime(2025, 11, 11, 12, 0, 0, tzinfo=pytz.UTC)
    lookback = get_lookback_time(hours=24, from_time=reference)

    assert isinstance(lookback, datetime)
    assert lookback < reference
    assert (reference - lookback).total_seconds() == 24 * 3600


def test_get_lookback_time_default():
    """Test lookback time with default (current time)."""
    lookback = get_lookback_time(hours=1)
    current = now()

    # Should be approximately 1 hour ago
    diff = (current - lookback).total_seconds()
    assert 3500 < diff < 3700  # Allow some margin


def test_format_friendly_date():
    """Test friendly date formatting."""
    dt = datetime(2025, 11, 11, 10, 30, 0, tzinfo=pytz.UTC)
    friendly = format_friendly_date(dt)

    assert isinstance(friendly, str)
    assert "November" in friendly or "Nov" in friendly
    assert "2025" in friendly


def test_is_market_open_weekend():
    """Test that market is closed on weekends."""
    # Saturday
    saturday = datetime(2025, 11, 8, 12, 0, 0, tzinfo=pytz.UTC)  # November 8, 2025 is a Saturday
    assert not is_market_open("US", saturday)

    # Sunday
    sunday = datetime(2025, 11, 9, 12, 0, 0, tzinfo=pytz.UTC)  # November 9, 2025 is a Sunday
    assert not is_market_open("US", sunday)


def test_get_market_hours():
    """Test market hours retrieval."""
    from src.utils.date_utils import get_market_hours

    dt = datetime(2025, 11, 11, 12, 0, 0, tzinfo=pytz.UTC)
    open_time, close_time = get_market_hours(dt, "US")

    assert isinstance(open_time, datetime)
    assert isinstance(close_time, datetime)
    assert open_time < close_time


def test_timezone_conversion():
    """Test timezone conversion in formatting."""
    dt_utc = datetime(2025, 11, 11, 12, 0, 0, tzinfo=pytz.UTC)
    formatted_paris = format_datetime(dt_utc, timezone="Europe/Paris")

    assert isinstance(formatted_paris, str)
    # Paris is UTC+1 or UTC+2, so hour should be different
    assert "12:00" not in formatted_paris or "CET" in formatted_paris or "CEST" in formatted_paris
