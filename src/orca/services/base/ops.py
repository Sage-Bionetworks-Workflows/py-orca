from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, Type, TypeVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from typing_extensions import Self

from orca.services.base.config import BaseConfig

ClientClass = TypeVar("ClientClass", bound=Any)

ConfigClass = TypeVar("ConfigClass", bound=BaseConfig)


@dataclass(kw_only=False, config=ConfigDict(arbitrary_types_allowed=True))
class BaseOps(ABC, Generic[ConfigClass, ClientClass]):
    """Base collection of operations for a service.

    N.B. Make sure to override the type hint for the ``client`` class
    variable in subclasses to enable pydantic validation.

    Attributes:
        client: An authenticated client object for this service.

    Class Variables:
        client_factory_class: The class for constructing clients.
    """

    client: ClientClass

    client_factory_class: ClassVar[Type]

    @classmethod
    @abstractmethod
    def from_config(cls, config: ConfigClass) -> Self:
        """Construct an Ops instance from the service configuration.

        Args:
            config: Service configuration.

        Returns:
            An Ops class instance for this service.
        """
