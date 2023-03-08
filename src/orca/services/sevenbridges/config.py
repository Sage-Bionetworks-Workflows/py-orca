from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, Any, Optional

from pydantic import validator
from pydantic.dataclasses import dataclass

from orca.services.base import BaseConfig

if TYPE_CHECKING:
    from airflow.models.connection import Connection


API_ENDPOINTS = {
    "https://api.sbgenomics.com/v2",
    "https://cgc-api.sbgenomics.com/v2",
    "https://cavatica-api.sbgenomics.com/v2",
}


@dataclass(kw_only=False)
class SevenBridgesConfig(BaseConfig):
    """Container class for SevenBridges-related configuration.

    Attributes:
        api_endpoint: API endpoint for a SevenBridges platform.
            Valid values are provided by the ``valid_api_endpoints``
            class variable.
        auth_token: An authentication token for the platform specified
            by the ``api_endpoints`` value.
        project: A SevenBridges project name (prefixed by username).
        client_kwargs: Keyword arguments for the SevenBridges Api class
            in the form of a dictionary.

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
    """

    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    project: Optional[str] = None
    client_kwargs: dict[str, Any] = field(default_factory=dict)

    connection_env_var = "SEVENBRIDGES_CONNECTION_URI"

    @validator("api_endpoint")
    def validate_api_endpoint(cls, value: str):
        """Validate the value of `api_endpoint`.

        Args:
            value: The SevenBridges API endpoint.

        Raises:
            ValueError: If the value isn't among the valid options.

        Returns:
            The input value, unchanged.
        """
        if value is not None and value not in API_ENDPOINTS:
            message = f"API endpoint ({value}) is not among {API_ENDPOINTS}."
            raise ValueError(message)
        return value

    @classmethod
    def parse_connection(cls, connection: Connection) -> dict[str, Any]:
        """Parse Airflow connection as arguments for this configuration.

        Args:
            connection: An Airflow connection object.

        Returns:
            Keyword arguments for this configuration.
        """
        api_endpoint = None
        if connection.host:
            schema = connection.schema or ""
            api_endpoint = f"https://{connection.host}/{schema}"
            api_endpoint = api_endpoint.rstrip("/")

        kwargs = {
            "api_endpoint": api_endpoint,
            "auth_token": connection.password,
            "project": connection.extra_dejson.get("project"),
        }
        return kwargs
