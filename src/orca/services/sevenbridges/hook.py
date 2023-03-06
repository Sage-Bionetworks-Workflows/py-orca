from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from airflow.exceptions import AirflowNotFoundException
from airflow.hooks.base import BaseHook
from sevenbridges import Api

from orca.services.sevenbridges.config import SevenBridgesConfig
from orca.services.sevenbridges.ops import SevenBridgesOps

if TYPE_CHECKING:
    from airflow.models.connection import Connection


class SevenBridgesHook(BaseHook):
    """Wrapper around SevenBridges client and ops classes.

    This hook was inspired by the Asana Airflow provider package:
    https://github.com/apache/airflow/blob/main/airflow/providers/asana/hooks/asana.py
    """

    conn_name_attr = "sbg_conn_id"
    default_conn_name = "sbg_default"
    conn_type = "sbg"
    hook_name = "SevenBridges"

    def __init__(self, conn_id: str = default_conn_name, *args, **kwargs):
        """Construct SevenBridgesHook using an Airflow connection.

        Args:
            conn_id: An Airflow connection ID.
                Defaults to ``default_conn_name``.
        """
        super().__init__(*args, **kwargs)
        self.connection = self.get_connection(conn_id)
        extras = self.connection.extra_dejson
        self.project = extras.get("project")

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
            connection = SevenBridgesConfig.get_connection_from_env()
        return connection

    def get_conn(self) -> SevenBridgesOps:
        """Retrieve the authenticated SevenBridgesOps object.

        This object contains an authenticated SevenBridges client.

        Returns:
            An authenticated SevenBridgesOps instance.
        """
        return self.ops

    @cached_property
    def client(self) -> Api:
        """Retrieve authenticated SevenBridges client."""
        return self.ops.client

    @cached_property
    def ops(self) -> SevenBridgesOps:
        """An authenticated SevenBridgesOps instance."""
        config = SevenBridgesConfig.from_connection(self.connection)
        return SevenBridgesOps.from_config(config)
