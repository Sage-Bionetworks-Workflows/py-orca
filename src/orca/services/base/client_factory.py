from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, ClassVar, Generic, Type, TypeVar

from pydantic.dataclasses import dataclass

from orca.errors import ClientRequestError
from orca.services.base.config import BaseConfig

ClientClass = TypeVar("ClientClass", bound=Any)

ConfigClass = TypeVar("ConfigClass", bound=BaseConfig)


@dataclass(kw_only=False)
class BaseClientFactory(ABC, Generic[ClientClass, ConfigClass]):
    """Base factory for constructing clients.

    Usage Instructions:
        1) Create a class that subclasses this base class.
        2) Decorate this class with ``@dataclass`` as this one does.
        3) Provide values to all class variables (defined below).
        4) Provide implementations for all abstract methods.
        5) Update the type hints for attributes and class variables.

    Attributes:
        config: Configuration object for this service.

    Class Variables:
        client_class: The client class for this service.
    """

    config: ConfigClass

    client_class: ClassVar[Type]

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
            client: An authenticated client object.
        """

    @classmethod
    def test_client(cls, client: ClientClass) -> None:
        """Test the client with an authenticated request.

        Args:
            client: An authenticated client object.

        Raises:
            ClientRequestError: If an error occured while making a request.
        """
        try:
            cls.test_client_request(client)
        except Exception as error:
            message = "Authenticated test request failed using the client."
            raise ClientRequestError(message) from error

    @cached_property
    def client(self) -> ClientClass:
        """An authenticated client."""
        return self.create_client()

    def get_client(self, test=False) -> ClientClass:
        """Retrieve (and optionally, test) an authenticated client.

        Args:
            test: Whether to test the client before returning it.

        Returns:
            An authenticated client.
        """
        client = self.client
        if test:
            self.test_client(client)
        return client
