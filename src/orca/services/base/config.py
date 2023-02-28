from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from pydantic.dataclasses import dataclass
from typing_extensions import Self

if TYPE_CHECKING:
    from airflow.models.connection import Connection


@dataclass(kw_only=False)
class BaseConfig(ABC):
    """Simple container class for service-related configuration.

    Class Variables:
        connection_env_var: The name of the environment variable whose
            value is an Airflow connection URI for this service.
    """

    connection_env_var: ClassVar[str]

    @classmethod
    @abstractmethod
    def from_connection(cls, connection: Connection) -> Self:
        """Parse Airflow connection as a service configuration.

        Args:
            connection: An Airflow connection object.

        Returns:
            Configuration relevant to this service.
        """

    @classmethod
    def from_env(cls) -> Self:
        """Parse environment as a service configuration.

        Args:
            connection: An Airflow connection object.

        Returns:
            Configuration relevant to this service.
        """
        # Short-circuit method if absent because Connection is slow-ish
        if cls.is_env_available():
            connection = cls.get_connection_from_env()
            config = cls.from_connection(connection)
        else:
            config = cls()
        return config

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
