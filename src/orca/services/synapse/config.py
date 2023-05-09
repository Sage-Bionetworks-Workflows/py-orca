from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from pydantic.dataclasses import dataclass

from orca.services.base.config import BaseConfig

if TYPE_CHECKING:
    from airflow.models.connection import Connection


@dataclass(kw_only=False)
class SynapseConfig(BaseConfig):
    """Simple container class for service-related configuration.

    Attributes:
        auth_token: A Synapse personal access token (PAT).

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
    """

    auth_token: Optional[str] = None

    connection_env_var = "SYNAPSE_CONNECTION_URI"

    @classmethod
    def parse_connection(cls, connection: Connection) -> dict[str, Any]:
        """Parse Airflow connection as arguments for this configuration.

        Args:
            connection: An Airflow connection object.

        Returns:
            Keyword arguments for this configuration.
        """
        return {"auth_token": connection.password}
