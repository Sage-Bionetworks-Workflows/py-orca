"""Convenience functions for constructing SevenBridges clients."""

from typing import Any

from sevenbridges import Api
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

__all__ = []

API_ENDPOINTS = frozenset(
    [
        "https://api.sbgenomics.com/v2",
        "https://cgc-api.sbgenomics.com/v2",
        "https://cavatica-api.sbgenomics.com/v2",
    ]
)


def init_client(api_endpoint: str, auth_token: str, **kwargs: Any) -> Api:
    """Construct SevenBridgesTasks from credentials.

    Args:
        api_endpoint: API base endpoint.
        auth_token: An authentication token. Available under the
            Developer menu.
        project: An owner-prefixed SevenBridges project.
            For example: <username>/<project-name>.
            Defaults to None.
        **kwargs: Additional keyword arguments that are passed to
            the SevenBridges client during its construction.

    Returns:
        An authenticated SevenBridgesTasks instance.
    """
    if api_endpoint not in API_ENDPOINTS:
        message = f"API ({api_endpoint}) is not among {API_ENDPOINTS}."
        raise ValueError(message)

    if not auth_token or not isinstance(auth_token, str):
        message = f"Auth token ({auth_token}) should be a string."
        raise ValueError(message)

    default_handlers = [rate_limit_sleeper, maintenance_sleeper]
    kwargs.setdefault("error_handlers", default_handlers)

    return Api(api_endpoint, auth_token, **kwargs)
