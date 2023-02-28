from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Generic, Type, TypeVar

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from orca.services.base.config import BaseServiceConfig

ClientClass = TypeVar("ClientClass", bound=Any)

ServiceConfig = TypeVar("ServiceConfig", bound=BaseServiceConfig)


@dataclass(kw_only=False)
class BaseClientFactory(ABC, Generic[ClientClass, ServiceConfig]):
    """Base factory for constructing clients."""

    # Using `__post_init_post_parse__()` to perform steps after validation
    def __post_init_post_parse__(self) -> None:
        """Resolve any attributes using the available methods."""
        self.resolve()

    @property
    @abstractmethod
    def config_class(self) -> Type[ServiceConfig]:
        """Service configuration class."""

    @property
    @abstractmethod
    def client_class(self) -> Type[ClientClass]:
        """Service client class."""

    @abstractmethod
    def update_with_config(self, config: ServiceConfig):
        """Update instance attributes based on client configuration.

        Args:
            config: Arguments relevant to this service.
        """

    @abstractmethod
    def validate(self) -> None:
        """Validate the currently available attributes.

        Raises:
            ClientAttrError: If one of the attributes is invalid.
        """

    @abstractmethod
    def prepare_client_kwargs(self) -> dict[str, Any]:
        """Prepare client keyword arguments.

        Returns:
            Dictionary of keyword arguments.
        """

    @staticmethod
    @abstractmethod
    def test_client(client: ClientClass) -> None:
        """Test the client with an authenticated request.

        Raises:
            ClientRequestError: If an error occured while making a request.
        """

    @classmethod
    def from_config(cls, config: ServiceConfig) -> Self:
        """Construct client factory from configuration.

        Args:
            config: Arguments relevant to this service.

        Returns:
            An instantiated client factory.
        """
        factory = cls()
        factory.update_with_config(config)
        return factory

    def resolve(self) -> None:
        """Resolve credentials based on priority.

        This method will update the attribute values (if applicable).
        """
        config = self.config_class.from_env()
        self.update_with_config(config)

    def create_client(self) -> ClientClass:
        """Create authenticated client using the available attributes.

        Returns:
            An authenticated client for this service.
        """
        self.validate()
        kwargs = self.prepare_client_kwargs()
        client = self.client_class(**kwargs)
        return client

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