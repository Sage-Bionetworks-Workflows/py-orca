from abc import ABC
from functools import cached_property
from typing import Any, ClassVar, Generic, Type, TypeVar

from pydantic.dataclasses import dataclass

from orca.services.base.config import BaseConfig

ClientClass = TypeVar("ClientClass", bound=Any)

ConfigClass = TypeVar("ConfigClass", bound=BaseConfig)


@dataclass(kw_only=False)
class BaseOps(ABC, Generic[ConfigClass, ClientClass]):
    """Base collection of operations for a service.

    N.B. Make sure to override the type hint for the ``client`` class
    variable in subclasses to enable pydantic validation.

    Attributes:
        client: An authenticated client object for this service.

    Class Variables:
        client_factory_class: The class for constructing clients.
    """

    config: ConfigClass

    client_factory_class: ClassVar[Type]

    @cached_property
    def client(self) -> ClientClass:
        """An authenticated client for this service"""
        factory = self.client_factory_class(self.config)
        return factory.get_client(test=True)
