from datetime import datetime


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO 8601 without fractional seconds."""
    dt_no_microseconds = dt.replace(microsecond=0)
    return dt_no_microseconds.isoformat()


def ensure_datetime(value: str | datetime | None) -> datetime | None:
    """Convert string to datetime if needed, pass through datetime objects.

    Args:
        value: A datetime object, ISO format string, or None

    Returns:
        datetime object or None

    Raises:
        TypeError: If value is not str, datetime, or None
    """
    if value is None:
        return None
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    if isinstance(value, datetime):
        return value
    raise TypeError(f"Expected str, datetime, or None, got {type(value).__name__}")
