import pytest
from sevenbridges import Api

from orca.services.sevenbridges import SevenBridgesHook, SevenBridgesOps


@pytest.mark.usefixtures("patch_get_connection")
class TestWithoutAirflow:
    def test_that_a_hook_can_be_constructed_from_a_connection(self, hook):
        assert isinstance(hook, SevenBridgesHook)

    def test_that_get_conn_return_client(self, hook):
        assert hook.get_conn() == hook.client

    def test_that_the_client_object_can_be_retrieved_from_hook(self, hook):
        assert isinstance(hook.client, Api)

    def test_that_the_ops_object_can_be_retrieved_from_hook(self, hook):
        assert isinstance(hook.ops, SevenBridgesOps)
