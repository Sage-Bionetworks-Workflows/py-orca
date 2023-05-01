from datetime import datetime, timezone


def parse_datetime(text: str) -> datetime:
    """Parse Tower datetime strings (RFC 3339).

    Args:
        text: Datetime string.

    Returns:
        Datetime object.
    """
    parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed
