import pytest
from pydantic.error_wrappers import ValidationError
from sevenbridges.errors import SbgError
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

from orca.errors import ClientRequestError, ConfigError


@pytest.mark.usefixtures("patch_os_environ")
class TestWithEmptyEnv:
    def test_for_an_error_when_using_unrecognized_api_endpoints(
        self, config, client_factory
    ):
        with pytest.raises(ValidationError):
            config = config.__class__("foo", "bar")
            client_factory.__class__(config)
        with pytest.raises(ValidationError):
            config = config.__class__("https://foo.sbgenomics.com/v2", "bar")
            client_factory.__class__(config)
        with pytest.raises(ValidationError):
            config = config.__class__("https://api.sbgenomics.com/v1", "bar")
            client_factory.__class__(config)

    def test_for_an_error_when_using_invalid_authentication_token(
        self, config, client_factory
    ):
        with pytest.raises(SbgError):
            config = config.__class__("https://api.sbgenomics.com/v2", "")
            client_factory.__class__(config).get_client()

    def test_for_an_error_when_missing_credentials(self, config, client_factory):
        with pytest.raises(ConfigError):
            config = config.__class__("https://api.sbgenomics.com/v2", None)
            client_factory.__class__(config).get_client()
        with pytest.raises(ConfigError):
            config = config.__class__(None, "bar")
            client_factory.__class__(config).get_client()

    def test_that_the_default_error_handlers_are_used(
        self, config, client_factory, mock_api_init
    ):
        factory = client_factory.__class__(config)
        factory.get_client()
        _, kwargs = mock_api_init.call_args
        assert "error_handlers" in kwargs
        handlers = kwargs["error_handlers"]
        assert maintenance_sleeper in handlers
        assert rate_limit_sleeper in handlers


def test_that_config_is_set(client_factory):
    client_factory_cls = client_factory.__class__
    assert getattr(client_factory_cls, "config", None) is not None


def test_that_client_class_is_set(client_factory):
    client_factory_cls = client_factory.__class__
    assert getattr(client_factory_cls, "client_class", None) is not None


def test_that_create_client_is_impl(client_factory):
    client = client_factory.create_client()
    assert client is not None


def test_that_create_client_throws_config_error_if_config_invalid(blank_client_factory):
    with pytest.raises(ConfigError):
        blank_client_factory.create_client()


def test_that_test_client_request_is_impl(client_factory):
    test_client_request = getattr(client_factory, "test_client_request", None)
    assert callable(test_client_request) is True


def test_that_test_client_throws_error_if_test_client_request_fails(client_factory):
    with pytest.raises(ClientRequestError):
        client_factory.test_client(client_factory.client)


def test_that_test_client_does_not_throws_error_if_test_client_request_passes(
    client_factory,
):
    client_factory.test_client(client_factory.client)


def test_that_get_client_calls_test_client_if_test():
    pass


def test_that_get_client_does_not_call_test_client_if_not_test():
    pass


def test_that_the_client_factory_class_is_called(patched_ops):
    mock_client_factory = patched_ops.client_factory_class
    patched_ops.client
    mock_client_factory.assert_called_once()


def test_that_get_client_method_is_called_at_most_once(patched_ops):
    mock_client_factory = patched_ops.client_factory_class
    patched_ops.client
    patched_ops.client
    mock_client_factory.return_value.get_client.assert_called_once_with(test=True)


@pytest.mark.integration
def test_that_a_valid_client_can_be_constructed_and_tested(
    config, client_factory, client_class
):
    # Authenticate using the environment variable
    factory = client_factory.__class__(config)
    client = factory.get_client(test=True)
    assert isinstance(client, client_class)


@pytest.mark.integration
def test_for_an_error_when_constructing_and_testing_an_invalid_client(
    config, client_factory
):
    # Authenticate using the environment variable
    factory = client_factory.__class__(config)
    with pytest.raises(ClientRequestError):
        factory.get_client(test=True)
