from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from typing_extensions import Self

from orca.services.base.config import BaseServiceConfig

ClientClass = TypeVar("ClientClass", bound=Any)

ServiceConfig = TypeVar("ServiceConfig", bound=BaseServiceConfig)


@dataclass(kw_only=False, config=ConfigDict(arbitrary_types_allowed=True))
class BaseOps(ABC, Generic[ServiceConfig, ClientClass]):
    """Base collection of operations for a service."""

    # Override this type hint in subclasses to enable pydantic validation
    client: ClientClass

    @classmethod
    @abstractmethod
    def from_config(cls, config: ServiceConfig) -> Self:
        """Construct an Ops instance from the service configuration.

        Args:
            config: Service configuration.

        Returns:
            An Ops class instance for this service.
        """
