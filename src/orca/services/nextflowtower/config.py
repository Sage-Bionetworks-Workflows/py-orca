from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from pydantic import validator
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
        workspace: A fully-qualified Nextflow Tower workspace name
            (i.e., prefixed with the organization name)
            (e.g., 'Sage-Bionetworks/example-project').

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
    """

    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    workspace: Optional[str] = None

    connection_env_var = "NEXTFLOWTOWER_CONNECTION_URI"

    @validator("workspace")
    def validate_workspace(cls, value: str):
        """Validate the value of `workspace`.

        Args:
            value: A fully-qualified Nextflow Tower workspace name.

        Raises:
            ValueError: If the value doesn't include two components
                separated by a forward slash.

        Returns:
            The input value, unchanged.
        """
        if value is None:
            return value
        org_name, _, workspace_name = value.partition("/")
        if not org_name or not workspace_name or "/" in workspace_name:
            structure = "<organization-name>/<workspace-name>"
            message = f"Workspace ({value}) should be structured as '{structure}'."
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
            "workspace": connection.extra_dejson.get("workspace"),
        }
        return kwargs
