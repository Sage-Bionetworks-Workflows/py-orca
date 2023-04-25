from orca.services.base import BaseConfig, BaseOps


def test_that_conn_name_attr_is_set(service):
    hook_cls = service["hook"]
    assert hasattr(hook_cls, "conn_name_attr")
    assert isinstance(hook_cls.conn_name_attr, str)


def test_that_default_conn_name_is_set(service):
    hook_cls = service["hook"]
    assert hasattr(hook_cls, "default_conn_name")
    assert isinstance(hook_cls.default_conn_name, str)


def test_that_conn_type_is_set(service):
    hook_cls = service["hook"]
    assert hasattr(hook_cls, "conn_type")
    assert isinstance(hook_cls.conn_type, str)


def test_that_hook_name_is_set(service):
    hook_cls = service["hook"]
    assert hasattr(hook_cls, "hook_name")
    assert isinstance(hook_cls.hook_name, str)


def test_that_ops_class_is_set(service):
    hook_cls = service["hook"]
    assert hasattr(hook_cls, "ops_class")
    assert issubclass(hook_cls.ops_class, BaseOps)


def test_that_config_class_is_set(service):
    hook_cls = service["hook"]
    assert hasattr(hook_cls, "config_class")
    assert issubclass(hook_cls.config_class, BaseConfig)
