from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Optional, Type, TypeVar

from airflow.exceptions import AirflowNotFoundException
from airflow.hooks.base import BaseHook

from orca.services.base.ops import BaseOps

if TYPE_CHECKING:
    from airflow.models.connection import Connection

ClientClass = TypeVar("ClientClass", bound=Any)

OpsClass = TypeVar("OpsClass", bound=BaseOps)


class BaseOrcaHook(BaseHook, Generic[OpsClass, ClientClass]):
    """Wrapper around client and ops classes.

    This base class is called 'BaseOrcaHook' to avoid confusion
    with the Airflow 'BaseHook' class, which this inherits from.

    This hook was inspired by the Asana Airflow provider package:
    https://github.com/apache/airflow/blob/main/airflow/providers/asana/hooks/asana.py

    Usage Instructions:
        1) Create a class that subclasses this base class.
        2) Provide values to all class variables (defined below).

    Class Variables:
        conn_name_attr: Inherited Airflow attribute (e.g., "sbg_conn_id").
        default_conn_name: Inherited Airflow attribute (e.g., "sbg_default").
        conn_type: Inherited Airflow attribute (e.g., "sbg").
        hook_name: Inherited Airflow attribute (e.g., "SevenBridges").
        ops_class: The Ops class for this service.
        config_class: The configuration class for this service.
    """

    conn_name_attr: ClassVar[str]
    default_conn_name: ClassVar[str]
    conn_type: ClassVar[str]
    hook_name: ClassVar[str]

    ops_class: ClassVar[Type]
    config_class: ClassVar[Type]

    def __init__(self, conn_id: Optional[str] = None, *args, **kwargs):
        """Construct hook using an Airflow connection.

        Args:
            conn_id: An Airflow connection ID.
                Defaults to ``default_conn_name``.
        """
        super().__init__(*args, **kwargs)
        conn_id = conn_id or self.default_conn_name
        self.connection = self.get_connection(conn_id)

    @classmethod
    def get_connection(cls, conn_id: str) -> Connection:
        """
        Retrieve Airflow connection

        Args:
            conn_id: Airflow connection ID.

        Returns:
            An Airflow connection.
        """
        try:
            connection = super().get_connection(conn_id)
        except AirflowNotFoundException:
            connection = cls.config_class.get_connection_from_env()
        return connection

    def get_conn(self) -> OpsClass:
        """Retrieve the authenticated Ops object.

        This object contains an authenticated client.

        Returns:
            An authenticated Ops object.
        """
        return self.ops

    @cached_property
    def client(self) -> ClientClass:
        """Retrieve authenticated client."""
        return self.ops.client

    @cached_property
    def ops(self) -> OpsClass:
        """An authenticated Ops object."""
        config = self.config_class.from_connection(self.connection)
        return self.ops_class(config)
