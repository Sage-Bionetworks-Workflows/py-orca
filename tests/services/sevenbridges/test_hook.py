import pytest
from airflow.models.connection import Connection
from sevenbridges import Api

from orca.errors import ConfigError
from orca.services.sevenbridges import SevenBridgesHook, SevenBridgesOps


@pytest.mark.usefixtures("patch_get_connection")
class TestWithoutAirflow:
    def test_that_a_hook_can_be_constructed_from_a_connection(self, hook):
        assert isinstance(hook, SevenBridgesHook)

    def test_that_get_conn_returns_ops_object(self, hook):
        assert hook.get_conn() == hook.ops

    def test_that_the_client_object_can_be_retrieved_from_hook(self, hook):
        assert isinstance(hook.client, Api)

    def test_that_the_ops_object_can_be_retrieved_from_hook(self, hook):
        assert isinstance(hook.ops, SevenBridgesOps)

    def test_that_a_connection_is_returned_without_airflow(self, hook):
        connection = hook.get_connection("foo")
        assert isinstance(connection, Connection)

    def test_for_error_without_airflow_or_env(
        self, hook, patch_get_connection, patch_os_environ, mocker
    ):
        empty_connection = Connection(uri="sbg://")
        mocker.patch.object(hook, "connection", empty_connection)
        with pytest.raises(ConfigError):
            hook.ops.client
