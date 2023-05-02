from collections.abc import Collection
from datetime import datetime, timezone
from typing import TypeVar

T = TypeVar("T", int, str)


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


def dedup(items: Collection[T]) -> list[T]:
    """Deduplicate items in a collection.

    Args:
        items: Collection of items.

    Returns:
        Deduplicated collection or None.
    """
    return list(set(items))
