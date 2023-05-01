from datetime import datetime


def parse_datetime(text: str) -> datetime:
    """Parse Tower datetime strings (RFC 3339).

    Args:
        text: Datetime string.

    Returns:
        Datetime object.
    """
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
