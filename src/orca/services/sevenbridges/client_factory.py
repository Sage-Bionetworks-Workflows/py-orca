from __future__ import annotations

from copy import deepcopy
from dataclasses import field
from typing import TYPE_CHECKING, Any, Optional, Type

from pydantic.dataclasses import dataclass
from sevenbridges import Api
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

from orca.errors import ClientAttrError, ClientRequestError
from orca.services.base import BaseClientFactory
from orca.services.sevenbridges.config import SevenBridgesConfig

API_ENDPOINTS = {
    "https://api.sbgenomics.com/v2",
    "https://cgc-api.sbgenomics.com/v2",
    "https://cavatica-api.sbgenomics.com/v2",
}


@dataclass(kw_only=False)
class SevenBridgesClientFactory(BaseClientFactory):
    """Factory for constructing SevenBridges clients.

    SevenBridges credentials can be provided in a few ways. The
    following methods are listed in order of decreasing prededence.

        Init parameters: You provide the API URL and authentication
            auth_token directly when you initialize this class.
        Environment variable: You provide an Airflow connection URI via
            an environment variable. The environment variable name is
            defined by `SevenBridgesConfig.connection_env_var`.

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

    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    client_kwargs: dict[str, Any] = field(default_factory=dict)

    @property
    def config_class(self) -> Type[SevenBridgesConfig]:
        """Service configuration class."""
        return SevenBridgesConfig

    @property
    def client_class(self) -> Type[Api]:
        """Service client class."""
        return Api

    def update_with_config(self, config: SevenBridgesConfig):
        """Update instance attributes based on client configuration.

        Args:
            config: Arguments relevant to this service.
        """
        self.api_endpoint = self.api_endpoint or config.api_endpoint
        self.auth_token = self.auth_token or config.auth_token

    def validate(self) -> None:
        """Validate the currently available attributes.

        Raises:
            ClientAttrError: If one of the attributes is invalid.
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
            raise ClientAttrError(common_message + addendum)

        if self.api_endpoint not in API_ENDPOINTS:
            addendum = f"API ({self.api_endpoint}) is not among {API_ENDPOINTS}."
            raise ClientAttrError(common_message + addendum)

    def prepare_client_kwargs(self) -> dict[str, Any]:
        """Prepare client keyword arguments.

        Returns:
            Dictionary of keyword arguments.
        """
        if TYPE_CHECKING:
            assert self.api_endpoint

        kwargs = deepcopy(self.client_kwargs)

        default_handlers = [rate_limit_sleeper, maintenance_sleeper]
        kwargs.setdefault("error_handlers", default_handlers)

        kwargs["url"] = self.api_endpoint.rstrip("/")
        kwargs["token"] = self.auth_token

        return kwargs

    @staticmethod
    def test_client(client: Api) -> None:
        """Test the client with an authenticated request.

        Raises:
            ClientRequestError: If an error occured while making a request.
        """
        try:
            client.users.me()
        except Exception as error:
            message = "Failed to retrieve active user information using the client."
            raise ClientRequestError(message) from error
