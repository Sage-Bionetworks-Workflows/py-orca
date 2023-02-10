import pytest
from airflow.models.connection import Connection
from sevenbridges import Api
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

from orca.errors import ClientArgsError, ClientRequestError
from orca.services.sevenbridges import SevenBridgesClientFactory


@pytest.mark.usefixtures("patch_os_environ")
class TestWithEmptyEnv:
    def test_for_an_error_when_using_unrecognized_api_endpoints(self):
        with pytest.raises(ClientArgsError):
            SevenBridgesClientFactory("foo", "bar")
        with pytest.raises(ClientArgsError):
            SevenBridgesClientFactory("https://foo.sbgenomics.com/v2", "bar")
        with pytest.raises(ClientArgsError):
            SevenBridgesClientFactory("https://api.sbgenomics.com/v1", "bar")

    def test_for_an_error_when_using_invalid_authentication_token(self):
        with pytest.raises(ClientArgsError):
            SevenBridgesClientFactory("https://api.sbgenomics.com/v2", "")

    def test_for_an_error_when_missing_credentials(self):
        with pytest.raises(ClientArgsError):
            SevenBridgesClientFactory("https://api.sbgenomics.com/v2", None)
        with pytest.raises(ClientArgsError):
            SevenBridgesClientFactory(None, "bar")

    def test_that_the_default_error_handlers_are_used(self, client_args, mock_api_init):
        factory = SevenBridgesClientFactory(**client_args)
        factory.get_client()
        _, kwargs = mock_api_init.call_args
        assert "error_handlers" in kwargs
        handlers = kwargs["error_handlers"]
        assert maintenance_sleeper in handlers
        assert rate_limit_sleeper in handlers


def test_that_a_nonempty_connection_can_be_mapped(connection, ops_args):
    actual = SevenBridgesClientFactory.parse_connection(connection)
    assert actual == ops_args


def test_that_an_empty_connection_can_be_mapped():
    expected = {"api_endpoint": None, "auth_token": None, "project": None}
    connection = Connection(uri="sbg://")
    result = SevenBridgesClientFactory.parse_connection(connection)
    assert result == expected


@pytest.mark.integration
def test_that_a_valid_client_can_be_constructed_and_tested():
    # Authenticate using the environment variable
    factory = SevenBridgesClientFactory()
    client = factory.get_and_test_client()
    assert isinstance(client, Api)


@pytest.mark.integration
def test_for_an_error_when_constructing_and_testing_an_invalid_client(client_args):
    # Authenticate using the environment variable
    factory = SevenBridgesClientFactory(client_args["api_endpoint"], "foo")
    with pytest.raises(ClientRequestError):
        factory.get_and_test_client()
