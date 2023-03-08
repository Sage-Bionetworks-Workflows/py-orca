from __future__ import annotations

from copy import deepcopy

from pydantic.dataclasses import dataclass
from sevenbridges import Api
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

from orca.errors import ConfigError
from orca.services.base import BaseClientFactory
from orca.services.sevenbridges.config import SevenBridgesConfig


@dataclass(kw_only=False)
class SevenBridgesClientFactory(BaseClientFactory):
    """Factory for constructing SevenBridges clients.

    By default, the client will be configured with two recommended
    error handlers, which are provided by the SevenBridges package:

        rate_limit_sleeper: Pause execution while the SevenBridges
            API indicates that the rate limit has been reached.
        maintenance_sleeper: Pause execution while the SevenBridges
            API is in maintenance mode.

    Attributes:
        config: Configuration object for this service.

    Class Variables:
        client_class: The client class for this service.
    """

    config: SevenBridgesConfig

    client_class = Api

    def create_client(self) -> Api:
        """Create an authenticated client.

        Typically, this involves pulling values from the configuration,
        ensuring that non-optional arguments are not set to None, and
        using them to instantiate a client class.

        Raises:
            ConfigError: If the configuration is invalid.

        Returns:
            An authenticated client object.
        """
        kwargs = deepcopy(self.config.client_kwargs)
        api_endpoint = self.config.api_endpoint
        auth_token = self.config.auth_token

        if api_endpoint is None or auth_token is None:
            message = f"Config ({self.config}) is missing api_endpoint or auth_token."
            raise ConfigError(message)

        default_handlers = [rate_limit_sleeper, maintenance_sleeper]
        kwargs.setdefault("error_handlers", default_handlers)

        kwargs["url"] = api_endpoint.rstrip("/")
        kwargs["token"] = auth_token

        return Api(**kwargs)

    @staticmethod
    def test_client_request(client: Api) -> None:
        """Make a test request with an authenticated request.

        This method does not need to perform any error handling.
        That is taken care of by the ``test_client()`` method.
        That said, this method can raise an error if a response
        is made but indicates a problem.

        Args:
            client: An authenticated client object.
        """
        client.users.me()
