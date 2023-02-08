from functools import cached_property

from airflow.hooks.base import BaseHook
from sevenbridges import Api

from orca.services.sevenbridges import SevenBridgesClientFactory, SevenBridgesTasks


class SevenBridgesHook(BaseHook):
    """Wrapper around SevenBridges client and tasks classes.

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

    def get_conn(self) -> Api:
        """Retrieve authenticated SevenBridges client."""
        return self.client

    @cached_property
    def client(self) -> Api:
        """Retrieve authenticated SevenBridges client."""
        client_args = SevenBridgesClientFactory.map_connection(self.connection)
        factory = SevenBridgesClientFactory(**client_args)
        return factory.get_client()

    @cached_property
    def tasks(self) -> SevenBridgesTasks:
        """Retrieve authenticated SevenBridgesTasks instance."""
        return SevenBridgesTasks(self.client, self.project)
