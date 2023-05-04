from dataclasses import fields
from typing import get_type_hints

from orca.services.base import BaseClientFactory, BaseConfig


def test_that_config_is_set(ops):
    assert hasattr(ops, "config")
    assert isinstance(ops.config, BaseConfig)


def test_that_config_has_a_default_factory(ops):
    config_field = [f for f in fields(ops) if f.name == "config"][0]
    assert getattr(config_field, "default_factory", None) is not None


def test_that_config_has_a_matching_default_factory(ops):
    config_field = [f for f in fields(ops) if f.name == "config"][0]
    config_type = get_type_hints(ops.__class__)["config"]
    assert config_field.default_factory == config_type


def test_that_client_factory_class_is_set(service):
    ops_class = service["ops"]
    assert hasattr(ops_class, "client_factory_class")
    assert issubclass(ops_class.client_factory_class, BaseClientFactory)


def test_that_a_client_can_be_accessed_from_ops_class(ops, mocker):
    mock = mocker.patch.object(ops.client_factory_class, "get_client")
    ops.client
    mock.assert_called_once()
