from __future__ import annotations

import os
from dataclasses import field
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Type

from pydantic.dataclasses import dataclass
from sevenbridges import Api
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

from orca.errors import ClientArgsError, ClientRequestError

if TYPE_CHECKING:
    from airflow.models.connection import Connection


@dataclass(kw_only=False)
class SevenBridgesClientFactory:
    """Factory for constructing SevenBridges clients.

    SevenBridges credentials can be provided in a few ways. The
    following methods are listed in order of decreasing prededence.
        Init parameters: You provide the API URL and authentication
            auth_token directly when you initialize this class.
        Environment variable: You provide an Airflow connection URI via
            an environment variable. The environment variable name is
            defined by `SevenBridgesClientFactory.CONNECTION_ENV`.

    By default, the client will be configured with two recommended
    error handlers, which are provided by the SevenBridges package:
        rate_limit_sleeper: Pause execution while the SevenBridges
            API indicates that the rate limit has been reached.
        maintenance_sleeper: Pause execution while the SevenBridges
            API is in maintenance mode.

    Attributes:
        api_endpoint: API base endpoint.
        auth_token: Authentication auth_token.
            Available under the Developer menu.
        client_kwargs: Additional keyword arguments that are passed to
            the SevenBridges client during its construction.
    """

    client_cls: ClassVar[Type]
    client_cls = Api

    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    client_kwargs: dict[str, Any] = field(default_factory=dict)

    CONNECTION_ENV = "SEVENBRIDGES_CONNECTION_URI"

    API_ENDPOINTS = {
        "https://api.sbgenomics.com/v2",
        "https://cgc-api.sbgenomics.com/v2",
        "https://cavatica-api.sbgenomics.com/v2",
    }

    # Using `__post_init_post_parse__()` to perform steps after validation
    def __post_init_post_parse__(self) -> None:
        """Resolve and validate credentials."""
        self.resolve_credentials()
        self.update_credentials()
        self.validate_credentials()
        self.update_client_kwargs()

    @staticmethod
    def parse_connection(connection: Connection) -> dict[str, Optional[str]]:
        """Map Airflow connection fields to keyword arguments.

        Args:
            connection: An Airflow connection object.

        Returns:
            Keyword arguments relevant to SevenBridges.
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

    @classmethod
    def connection_from_env(cls) -> Connection:
        """Generate Airflow connection from environment variable.

        Returns:
            An Airflow connection
        """
        # Following Airflow's lead on this non-standard practice
        # because this import does introduce a bit of overhead
        from airflow.models.connection import Connection

        env_connection_uri = os.environ.get(cls.CONNECTION_ENV)
        return Connection(uri=env_connection_uri)

    @classmethod
    def kwargs_from_env(cls) -> dict[str, Optional[str]]:
        """Parse environment variable for keyword arguments.

        Returns:
            Keyword arguments relevant to SevenBridges.
        """
        env_connection = cls.connection_from_env()
        return cls.parse_connection(env_connection)

    def resolve_credentials(self) -> None:
        """Resolve SevenBridges credentials based on priority.

        This method will update the attribute values (if applicable).
        """
        # Short-circuit method if absent because Connection is slow-ish
        if os.environ.get(self.CONNECTION_ENV) is None:
            return

        # Get value from environment, which is confirmed to be available
        env_kwargs = self.kwargs_from_env()

        # Resolve single values for each client argument based on priority
        self.api_endpoint = self.api_endpoint or env_kwargs["api_endpoint"]
        self.auth_token = self.auth_token or env_kwargs["auth_token"]

    def update_credentials(self) -> None:
        """Update credentials for consistency."""
        if isinstance(self.api_endpoint, str):
            self.api_endpoint = self.api_endpoint.rstrip("/")

    def validate_credentials(self) -> None:
        """Validate the currently available credential attributes.

        Raises:
            ClientArgsError: If one of the required values is unset (None).
            ClientArgsError: If the API URL is not among the valid values.
            ClientArgsError: If the authentication auth_token is not a string.
        """
        # Prepare a common error message for the entire function
        common_message = (
            "Missing or invalid credentials: "
            f"api_endpoint = '{self.api_endpoint}' and "
            f"auth_token = '{self.auth_token}'. "
        )

        if self.api_endpoint is None or self.auth_token is None:
            addendum = (
                "One of the resolved values is unset (None). Review "
                "the class docstring to learn about methods for "
                "providing SevenBridges credentials."
            )
            raise ClientArgsError(common_message + addendum)

        if self.api_endpoint not in self.API_ENDPOINTS:
            addendum = f"API ({self.api_endpoint}) is not among {self.API_ENDPOINTS}."
            raise ClientArgsError(common_message + addendum)

        if not self.auth_token or not isinstance(self.auth_token, str):
            addendum = f"Auth auth_token ({self.auth_token}) should be a string."
            raise ClientArgsError(common_message + addendum)

    def update_client_kwargs(self) -> None:
        """Update client keyword arguments with default values."""
        default_handlers = [rate_limit_sleeper, maintenance_sleeper]
        self.client_kwargs.setdefault("error_handlers", default_handlers)

    @cached_property
    def _client(self) -> Api:
        """An authenticated SevenBridges client."""
        return self.client_cls(self.api_endpoint, self.auth_token, **self.client_kwargs)

    def get_client(self) -> Api:
        """Retrieve an authenticated SevenBridges client.

        Returns:
            An authenticated SevenBridges client.
        """
        return self._client

    def get_and_test_client(self) -> Api:
        """Retrieve and test an authenticated SevenBridges client.

        Returns:
            An authenticated SevenBridges client.
        """
        client = self.get_client()
        self.test_client(client)
        return client

    @staticmethod
    def test_client(client: Api) -> None:
        """Test the client with an authenticated request.

        Raises:
            ClientRequestError: If any error arises during the test.
        """
        try:
            client.users.me()
        except Exception as error:
            message = "Failed to retrieve active user information using the client."
            raise ClientRequestError(message) from error
