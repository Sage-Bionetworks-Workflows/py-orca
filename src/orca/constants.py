from typing import Any

from pydantic import ConfigDict


def dataclass_kwargs() -> dict[str, Any]:
    """Generate reasonable default arguments for dataclass.

    A function is used to overcome the mutability of dictionaries.

    Returns:
        Keyword arguments for dataclass.
    """
    kwargs = {
        "config": ConfigDict(arbitrary_types_allowed=True),
        "kw_only": False,
    }
    return kwargs
