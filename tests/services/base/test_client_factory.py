import pytest

from orca.errors import ClientRequestError, ConfigError
from orca.services.base import BaseConfig


def test_that_config_is_set(client_factory):
    assert hasattr(client_factory, "config")
    assert isinstance(client_factory.config, BaseConfig)


def test_that_client_class_is_set(service):
    client_factory_cls = service["client_factory"]
    assert hasattr(client_factory_cls, "client_class")


def test_that_client_factory_can_generate_client(client_factory):
    client = client_factory.create_client()
    assert isinstance(client, client_factory.client_class)


def test_for_an_error_when_testing_the_client_without_auth(client_factory):
    client = client_factory.create_client()
    with pytest.raises(ClientRequestError):
        client_factory.test_client(client)


def test_that_create_client_throws_config_error_if_config_invalid(service):
    config_cls = service["config"]
    client_factory_cls = service["client_factory"]
    config = config_cls()
    client_factory = client_factory_cls(config)
    with pytest.raises(ConfigError):
        client_factory.create_client()


def test_that_get_client_calls_test_client_if_test_is_enabled(client_factory, mocker):
    mock = mocker.patch.object(client_factory, "test_client")
    client_factory.get_client(test=True)
    mock.assert_called_once()


def test_that_get_client_calls_test_client_if_test_is_disabled(client_factory, mocker):
    mock = mocker.patch.object(client_factory, "test_client")
    client_factory.get_client(test=False)
    mock.assert_not_called()
