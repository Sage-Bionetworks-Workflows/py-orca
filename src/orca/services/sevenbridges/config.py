from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic.dataclasses import dataclass

from orca.services.base import BaseServiceConfig

if TYPE_CHECKING:
    from airflow.models.connection import Connection


@dataclass(kw_only=False)
class SevenBridgesConfig(BaseServiceConfig):
    """Container class for SevenBridges-related configuration."""

    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    project: Optional[str] = None

    connection_env_var = "SEVENBRIDGES_CONNECTION_URI"

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
