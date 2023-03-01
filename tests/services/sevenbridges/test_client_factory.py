import pytest
from airflow.models.connection import Connection
from pydantic.error_wrappers import ValidationError
from sevenbridges import Api
from sevenbridges.errors import SbgError
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

from orca.errors import ClientRequestError, ConfigError
from orca.services.sevenbridges.client_factory import (
    SevenBridgesClientFactory,
    SevenBridgesConfig,
)


@pytest.mark.usefixtures("patch_os_environ")
class TestWithEmptyEnv:
    def test_for_an_error_when_using_unrecognized_api_endpoints(self):
        with pytest.raises(ValidationError):
            config = SevenBridgesConfig("foo", "bar")
            SevenBridgesClientFactory(config)
        with pytest.raises(ValidationError):
            config = SevenBridgesConfig("https://foo.sbgenomics.com/v2", "bar")
            SevenBridgesClientFactory(config)
        with pytest.raises(ValidationError):
            config = SevenBridgesConfig("https://api.sbgenomics.com/v1", "bar")
            SevenBridgesClientFactory(config)

    def test_for_an_error_when_using_invalid_authentication_token(self):
        with pytest.raises(SbgError):
            config = SevenBridgesConfig("https://api.sbgenomics.com/v2", "")
            SevenBridgesClientFactory(config).get_client()

    def test_for_an_error_when_missing_credentials(self):
        with pytest.raises(ConfigError):
            config = SevenBridgesConfig("https://api.sbgenomics.com/v2", None)
            SevenBridgesClientFactory(config).get_client()
        with pytest.raises(ConfigError):
            config = SevenBridgesConfig(None, "bar")
            SevenBridgesClientFactory(config).get_client()

    def test_that_the_default_error_handlers_are_used(self, config, mock_api_init):
        factory = SevenBridgesClientFactory(config)
        factory.get_client()
        _, kwargs = mock_api_init.call_args
        assert "error_handlers" in kwargs
        handlers = kwargs["error_handlers"]
        assert maintenance_sleeper in handlers
        assert rate_limit_sleeper in handlers


def test_that_a_nonempty_connection_can_be_mapped(connection, config):
    actual = SevenBridgesConfig.from_connection(connection)
    expected = config
    assert actual == expected


def test_that_an_empty_connection_can_be_mapped():
    expected = SevenBridgesConfig()
    connection = Connection(uri="sbg://")
    result = SevenBridgesConfig.from_connection(connection)
    assert result == expected


@pytest.mark.integration
def test_that_a_valid_client_can_be_constructed_and_tested():
    # Authenticate using the environment variable
    config = SevenBridgesConfig()
    factory = SevenBridgesClientFactory(config)
    client = factory.get_client(test=True)
    assert isinstance(client, Api)


@pytest.mark.integration
def test_for_an_error_when_constructing_and_testing_an_invalid_client(config):
    # Authenticate using the environment variable
    factory = SevenBridgesClientFactory(config)
    with pytest.raises(ClientRequestError):
        factory.get_client(test=True)
