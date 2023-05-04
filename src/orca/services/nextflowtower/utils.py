from collections.abc import Collection
from datetime import datetime, timezone
from typing import Any, TypeVar

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


def increment_suffix(text: str, separator: str = "_") -> str:
    """Increment integer suffix for a string.

    Args:
        text: Text (already integer-suffixed or not).
        separator: Separator between text and suffix.
            Defaults to underscore.

    Returns:
        Incremented suffixed text.
    """
    prefix, sep, suffix = text.rpartition(separator)
    # "foo".rpartition("_")  ->  ('', '', 'foo')
    if sep == "":
        return f"{text}{separator}2"
    # "foo_".rpartition("_")  ->  ('foo', '_', '')
    elif suffix == "":
        return f"{text}2"
    # "foo_1".rpartition("_")  ->  ('foo', '_', '1')
    elif suffix.isdigit():
        suffix_int = int(suffix)
        incremented = suffix_int + 1
        return f"{prefix}{sep}{incremented}"
    # "foo_bar".rpartition("_")  ->  ('foo', '_', 'bar')
    else:
        return f"{text}{separator}2"


def get_nested(dictionary: dict[str, Any], keys: str) -> Any:
    """Retrieve nested value in a dictionary.

    Args:
        dictionary: Dictionary (nested or not).
        keys: Period-delimited list of keys
            (one per dictionary level).

    Raises:
        ValueError: If the keys don't resolve to a value.

    Returns:
        Nested value corresponding to the list of keys.
    """
    target = dictionary
    for api_name_part in keys.split("."):
        if api_name_part not in target:
            message = f"Keys ({keys}) don't resolve to a value in: {dictionary}"
            raise ValueError(message)
        target = target[api_name_part]
    return target
