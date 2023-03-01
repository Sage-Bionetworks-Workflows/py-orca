from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from pydantic.dataclasses import dataclass

from orca.services.base.config import BaseConfig

if TYPE_CHECKING:
    from airflow.models.connection import Connection


@dataclass(kw_only=False)
class NextflowTowerConfig(BaseConfig):
    """Simple container class for service-related configuration.

    Attributes:
        api_endpoint: API endpoint for a Nextflow Tower platform.
        auth_token: An authentication token for the platform specified
            by the ``api_endpoints`` value.
        workspace: A Nextflow Tower workspace ID.

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
    """

    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    workspace: Optional[int] = None

    connection_env_var = "NEXTFLOWTOWER_CONNECTION_URI"

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
            "workspace": connection.extra_dejson.get("workspace"),
        }
        return kwargs
