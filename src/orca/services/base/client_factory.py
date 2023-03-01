from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Generic, TypeVar

from pydantic.dataclasses import dataclass

from orca.errors import ClientRequestError
from orca.services.base.config import BaseConfig

ClientClass = TypeVar("ClientClass", bound=Any)

ConfigClass = TypeVar("ConfigClass", bound=BaseConfig)


@dataclass(kw_only=False)
class BaseClientFactory(ABC, Generic[ClientClass, ConfigClass]):
    """Base factory for constructing clients.

    Attributes:
        config: Configuration relevant to this service.

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
    """

    config: ConfigClass

    @abstractmethod
    def create_client(self) -> ClientClass:
        """Create an authenticated client.

        Typically, this involves pulling values from the configuration,
        ensuring that non-optional arguments are not set to None, and
        using them to instantiate a client class.

        Raises:
            ConfigError: If the configuration is invalid.

        Returns:
            An authenticated client object.
        """

    @classmethod
    @abstractmethod
    def test_client_request(cls, client: ClientClass) -> None:
        """Make a test request with an authenticated request.

        This method does not need to perform any error handling.
        That is taken care of by the ``test_client()`` method.
        That said, this method can raise an error if a response
        is made but indicates a problem.

        Args:
            An authenticated instance of the client for this service.
        """

    @classmethod
    def test_client(cls, client: ClientClass) -> None:
        """Test the client with an authenticated request.

        Args:
            An authenticated instance of the client for this service.

        Raises:
            ClientRequestError: If an error occured while making a request.
        """
        try:
            cls.test_client_request(client)
        except Exception as error:
            message = "Authenticated test request failed using the client."
            raise ClientRequestError(message) from error

    @cached_property
    def _client(self) -> ClientClass:
        """An authenticated client."""
        return self.create_client()

    def get_client(self, test=False) -> ClientClass:
        """Retrieve (and optionally, test) an authenticated client.

        Args:
            test: Whether to test the client before returning it.

        Returns:
            An authenticated client.
        """
        client = self._client
        if test:
            self.test_client(client)
        return client
