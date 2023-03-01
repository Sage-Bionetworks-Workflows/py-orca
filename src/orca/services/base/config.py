from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import fields
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic.dataclasses import dataclass
from typing_extensions import Self

if TYPE_CHECKING:
    from airflow.models.connection import Connection


@dataclass(kw_only=False)
class BaseConfig(ABC):
    """Simple container class for service-related configuration.

    Usage Instructions:
        1) Create a class that subclasses this base class.
        2) Decorate this class with ``@dataclass`` as this one does.
        3) Provide values to all class variables (defined below).
        4) Provide implementations for all abstract methods.
        5) Verify that the assumptions defined below are met.
        6) (Optional) Implement custom Pydantic validators

    Assumptions:
        This base class assumes that all attributes are optional. It is
            the responsibility of the calling context to ensure that a
            configuration instance has the values it needs.

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
    """

    connection_env_var: ClassVar[str]

    @classmethod
    @abstractmethod
    def parse_connection(cls, connection: Connection) -> dict[str, Any]:
        """Parse Airflow connection as arguments for this configuration.

        Args:
            connection: An Airflow connection object.

        Returns:
            Keyword arguments for this configuration.
        """

    @classmethod
    def from_connection(cls, connection: Connection) -> Self:
        """Parse Airflow connection as a service configuration.

        Args:
            connection: An Airflow connection object.

        Returns:
            Configuration relevant to this service.
        """
        kwargs = cls.parse_connection(connection)
        return cls(**kwargs)

    def __post_init_post_parse__(self) -> None:
        """Resolve any attributes using the available methods.

        This method is run after pydantic validation:
        https://docs.pydantic.dev/usage/dataclasses/#initialize-hooks
        """
        self.resolve()

    def resolve(self) -> None:
        """Resolve credentials based on priority.

        This method will update the attribute values (if applicable).
        """
        if self.is_env_available():
            env_connection = self.get_connection_from_env()
            env_kwargs = self.parse_connection(env_connection)
            self.fill_in(env_kwargs)

    def fill_in(self, kwargs: dict[str, Any]) -> None:
        """Fill in missing attributes with another configuration.

        Args:
            kwargs: Keyword arguments for this configuration.
        """
        for field in fields(self):
            name = field.name
            if getattr(self, name, None) is None:
                other_value = kwargs.get(name, None)
                setattr(self, name, other_value)

    @classmethod
    def get_connection_from_env(cls) -> Connection:
        """Generate Airflow connection from environment variable.

        Returns:
            An Airflow connection
        """
        # Following Airflow's lead on this non-standard practice
        # because this import does introduce a bit of overhead
        from airflow.models.connection import Connection

        env_connection_uri = os.environ.get(cls.connection_env_var)
        return Connection(uri=env_connection_uri)

    @classmethod
    def is_env_available(cls) -> bool:
        """Check if the connection environment variable is available.

        Returns:
            Whether the connection environment variable is available.
        """
        return os.environ.get(cls.connection_env_var) is not None
