from functools import cached_property
from typing import Any, ClassVar, Generic, Type, TypeVar

from pydantic.dataclasses import dataclass

from orca.services.base.config import BaseConfig

ClientClass = TypeVar("ClientClass", bound=Any)

ConfigClass = TypeVar("ConfigClass", bound=BaseConfig)


@dataclass(kw_only=False)
class BaseOps(Generic[ConfigClass, ClientClass]):
    """Base collection of operations for a service.

    Usage Instructions:
        1) Create a class that subclasses this base class.
        2) Decorate this class with ``@dataclass`` as this one does.
        3) Provide values to all class variables (defined below).
        4) Provide implementations for all abstract methods.
        5) Update the type hints for attributes and class variables.
        6) Update the config attribute to have a default factory set to
           the config class using the `dataclasses.field()` function.

    Attributes:
        config: A configuration object for this service.

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
