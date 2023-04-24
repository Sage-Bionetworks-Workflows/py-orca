from dataclasses import fields

from airflow.models.connection import Connection


def test_that_connection_env_var_is_set(service):
    config_cls = service["config"]
    assert hasattr(config_cls, "connection_env_var")
    assert isinstance(config_cls.connection_env_var, str)
    assert config_cls.connection_env_var.endswith("_CONNECTION_URI")


def test_that_config_can_parse_connection(service):
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    connection = Connection(uri=connection_uri)
    params = config_cls.parse_connection(connection)
    for param_name in params:
        assert hasattr(config_cls, param_name)


def test_that_a_config_can_be_created_from_a_connection(service):
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    connection = Connection(uri=connection_uri)
    config = config_cls.from_connection(connection)
    assert isinstance(config, config_cls)


def test_that_config_can_pull_connection_uri_from_env(service, mocker):
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    env_var = config_cls.connection_env_var
    mocker.patch("os.environ", {env_var: connection_uri})
    config = config_cls()
    for field in fields(config_cls):
        assert getattr(config, field.name) is not None


def test_that_config_has_default_values_when_created_in_vacuum(service):
    config_cls = service["config"]
    config = config_cls()
    for field in fields(config_cls):
        assert hasattr(config, field.name)


def test_that_config_can_create_connection_from_env_var(service, mocker):
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    env_var = config_cls.connection_env_var
    mocker.patch("os.environ", {env_var: connection_uri})
    connection = config_cls.get_connection_from_env()
    assert isinstance(connection, Connection)


def test_that_is_env_available_returns_false_with_empty_env(service):
    config_cls = service["config"]
    assert not config_cls.is_env_available()


def test_that_is_env_available_returns_true_with_nonempty_env(service, mocker):
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    env_var = config_cls.connection_env_var
    mocker.patch("os.environ", {env_var: connection_uri})
    assert config_cls.is_env_available()
