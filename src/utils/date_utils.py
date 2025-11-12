"""
Date and time utilities for ZenMarket AI.
Handles timezone-aware datetime operations.
"""

from datetime import datetime, timedelta

import pytz


def get_timezone(tz_name: str = "Europe/Paris") -> pytz.timezone:
    """
    Get timezone object.

    Args:
        tz_name: Timezone name (e.g., 'Europe/Paris', 'America/New_York')

    Returns:
        Timezone object
    """
    try:
        return pytz.timezone(tz_name)
    except pytz.exceptions.UnknownTimeZoneError:
        return pytz.UTC


def now(timezone: str | None = None) -> datetime:
    """
    Get current datetime in specified timezone.

    Args:
        timezone: Timezone name. If None, uses UTC.

    Returns:
        Timezone-aware datetime
    """
    tz = get_timezone(timezone) if timezone else pytz.UTC
    return datetime.now(tz)


def format_datetime(
    dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S %Z", timezone: str | None = None
) -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime object
        fmt: Format string
        timezone: Target timezone. If None, uses datetime's timezone.

    Returns:
        Formatted datetime string
    """
    if timezone:
        tz = get_timezone(timezone)
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        dt = dt.astimezone(tz)

    return dt.strftime(fmt)


def parse_datetime(
    dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S", timezone: str | None = None
) -> datetime:
    """
    Parse datetime string.

    Args:
        dt_str: Datetime string
        fmt: Format string
        timezone: Timezone to apply. If None, assumes UTC.

    Returns:
        Timezone-aware datetime
    """
    dt = datetime.strptime(dt_str, fmt)
    tz = get_timezone(timezone) if timezone else pytz.UTC

    if dt.tzinfo is None:
        dt = tz.localize(dt)

    return dt


def get_market_hours(date: datetime | None = None, market: str = "US") -> tuple[datetime, datetime]:
    """
    Get market trading hours for a specific date.

    Args:
        date: Date to check. If None, uses today.
        market: Market identifier ('US', 'EU', 'ASIA')

    Returns:
        Tuple of (open_time, close_time)
    """
    if date is None:
        date = now()

    # Market hours in local time
    market_hours = {
        "US": ("09:30", "16:00", "America/New_York"),
        "EU": ("09:00", "17:30", "Europe/Paris"),
        "ASIA": ("09:00", "15:00", "Asia/Tokyo"),
    }

    if market not in market_hours:
        market = "US"

    open_str, close_str, tz_name = market_hours[market]
    tz = get_timezone(tz_name)

    date_str = date.strftime("%Y-%m-%d")
    open_time = tz.localize(datetime.strptime(f"{date_str} {open_str}", "%Y-%m-%d %H:%M"))
    close_time = tz.localize(datetime.strptime(f"{date_str} {close_str}", "%Y-%m-%d %H:%M"))

    return open_time, close_time


def is_market_open(market: str = "US", dt: datetime | None = None) -> bool:
    """
    Check if market is currently open.

    Args:
        market: Market identifier
        dt: Datetime to check. If None, uses now.

    Returns:
        True if market is open
    """
    if dt is None:
        dt = now()

    # Weekend check
    if dt.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    open_time, close_time = get_market_hours(dt, market)

    # Convert to same timezone
    if dt.tzinfo != open_time.tzinfo:
        dt = dt.astimezone(open_time.tzinfo)

    return open_time <= dt <= close_time


def get_lookback_time(hours: int = 24, from_time: datetime | None = None) -> datetime:
    """
    Get datetime N hours ago.

    Args:
        hours: Number of hours to look back
        from_time: Reference time. If None, uses now.

    Returns:
        Datetime N hours ago
    """
    if from_time is None:
        from_time = now()

    return from_time - timedelta(hours=hours)


def format_friendly_date(dt: datetime) -> str:
    """
    Format datetime in friendly format for reports.

    Args:
        dt: Datetime object

    Returns:
        Friendly formatted string (e.g., "Monday, January 15, 2025 - 09:30 AM")
    """
    return dt.strftime("%A, %B %d, %Y - %I:%M %p %Z")
