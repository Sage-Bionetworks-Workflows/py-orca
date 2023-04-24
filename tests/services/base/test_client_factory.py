import pytest

from orca.errors import ClientRequestError, ConfigError


def test_that_config_is_set(client_factory):
    client_factory_cls = client_factory.__class__
    assert getattr(client_factory_cls, "config", None) is not None


def test_that_client_class_is_set(client_factory):
    client_factory_cls = client_factory.__class__
    assert getattr(client_factory_cls, "client_class", None) is not None


def test_that_create_client_is_implemented(client_factory):
    client = client_factory.create_client()
    assert client is not None


def test_that_create_client_throws_config_error_if_config_invalid(blank_client_factory):
    with pytest.raises(ConfigError):
        blank_client_factory.create_client()


def test_that_test_client_request_is_implemented(client_factory):
    test_client_request = getattr(client_factory, "test_client_request", None)
    assert callable(test_client_request) is True


def test_that_test_client_throws_error_if_test_client_request_fails(client_factory):
    with pytest.raises(ClientRequestError):
        client_factory.test_client(client_factory.client)


def test_that_test_client_does_not_throws_error_if_test_client_request_passes(
    client_factory,
):
    client_factory.test_client(client_factory.client)


def test_that_get_client_calls_test_client_if_test(patched_ops):
    mock_client_factory = patched_ops.client_factory_class
    patched_ops.client_factory_class.get_client
    mock_client_factory.assert_called_once(test=True)


def test_that_get_client_does_not_call_test_client_if_not_test(patched_ops):
    mock_client_factory = patched_ops.client_factory_class
    patched_ops.client_factory_class.get_client
    mock_client_factory.assert_not_called()


@pytest.mark.integration
def test_that_a_valid_client_can_be_constructed_and_tested(
    config, client_factory, client_class
):
    # NOTE: borrowed this from the seven bridges test, not sure if applicable
    # Authenticate using the environment variable
    factory = client_factory.__class__(config)
    client = factory.get_client(test=True)
    assert isinstance(client, client_class)


@pytest.mark.integration
def test_for_an_error_when_constructing_and_testing_an_invalid_client(
    config, client_factory
):
    # NOTE: borrowed this from the seven bridges test, not sure if applicable
    # Authenticate using the environment variable
    factory = client_factory.__class__(config)
    with pytest.raises(ClientRequestError):
        factory.get_client(test=True)
