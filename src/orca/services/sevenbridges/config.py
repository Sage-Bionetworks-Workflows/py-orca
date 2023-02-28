from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional

from pydantic.dataclasses import dataclass

from orca.services.base import BaseConfig

if TYPE_CHECKING:
    from airflow.models.connection import Connection


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

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
        api_endpoints: The set of currently supported API endpoints.
    """

    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    project: Optional[str] = None

    connection_env_var = "SEVENBRIDGES_CONNECTION_URI"

    valid_api_endpoints: ClassVar[set[str]] = {
        "https://api.sbgenomics.com/v2",
        "https://cgc-api.sbgenomics.com/v2",
        "https://cavatica-api.sbgenomics.com/v2",
    }

    @classmethod
    def from_connection(cls, connection: Connection) -> SevenBridgesConfig:
        """Parse Airflow connection as a service configuration.

        Args:
            connection: An Airflow connection object.

        Returns:
            Configuration relevant to this service.
        """
        api_endpoint = None
        if connection.host:
            schema = connection.schema or ""
            api_endpoint = f"https://{connection.host}/{schema}"
            api_endpoint = api_endpoint.rstrip("/")

        config = cls(
            api_endpoint=api_endpoint,
            auth_token=connection.password,
            project=connection.extra_dejson.get("project"),
        )
        return config
