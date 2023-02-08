import pytest

from orca.services.sevenbridges import SevenBridgesTasks


@pytest.mark.usefixtures("patch_os_environ")
class TestWithEmptyEnv:
    def test_that_constructions_from_creds_works(self, client_creds, api_mock):
        SevenBridgesTasks.from_creds(**client_creds)
        api_mock.assert_called_once()
