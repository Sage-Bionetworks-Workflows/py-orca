from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from sevenbridges import Api

from orca.services.sevenbridges import SevenBridgesClientFactory


@dataclass
class SevenBridgesTasks:
    """Common tasks for SevenBridges platforms.

    Attributes:
        client: An authenticated SevenBridges client.
        project: A SevenBridges project (prefixed by username).
    """

    client: Api
    project: Optional[str] = None

    @classmethod
    def from_creds(
        cls,
        api_endpoint: str,
        auth_token: str,
        project: Optional[str] = None,
        **client_kwargs: Any,
    ) -> SevenBridgesTasks:
        """Construct SevenBridgesTasks from credentials.

        Args:
            api_endpoint: API base endpoint.
            auth_token: An authentication token. Available under the
                Developer menu.
            project: An owner-prefixed SevenBridges project.
                For example: <username>/<project-name>.
                Defaults to None.
            **client_kwargs: Additional keyword arguments that are passed
                to the SevenBridges client during its construction.

        Returns:
            An authenticated SevenBridgesTasks instance.
        """
        factory = SevenBridgesClientFactory(api_endpoint, auth_token, client_kwargs)
        client = factory.get_client()
        return SevenBridgesTasks(client, project)
