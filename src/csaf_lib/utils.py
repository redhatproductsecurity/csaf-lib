from datetime import datetime


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO 8601 without fractional seconds."""
    dt_no_microseconds = dt.replace(microsecond=0)
    return dt_no_microseconds.isoformat()
