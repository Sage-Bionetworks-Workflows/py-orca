from orca.services.base import BaseClientFactory, BaseConfig


def test_that_config_is_set(ops):
    assert hasattr(ops, "config")
    assert isinstance(ops.config, BaseConfig)


def test_that_client_factory_class_is_set(service):
    ops_class = service["ops"]
    assert hasattr(ops_class, "client_factory_class")
    assert issubclass(ops_class.client_factory_class, BaseClientFactory)


def test_that_a_client_can_be_accessed_from_ops_class(ops, mocker):
    mock = mocker.patch.object(ops.client_factory_class, "get_client")
    ops.client
    mock.assert_called_once()
