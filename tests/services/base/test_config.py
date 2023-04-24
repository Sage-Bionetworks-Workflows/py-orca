from dataclasses import fields

from airflow.models.connection import Connection


def test_that_connection_env_var_is_set(config):
    config_cls = config.__class__
    assert getattr(config_cls, "connection_env_var", None) is not None


def test_that_parse_connection_is_implemented(config, connection):
    """Tests that parse_connection is implemented
    Returns a value no error, doesn't matter the value
    """
    kwargs = config.parse_connection(connection)
    assert kwargs is not None, "parse_connection returns no configuration"


def test_that_a_nonempty_connection_can_be_mapped(config, connection):
    actual = config.__class__.from_connection(connection)
    expected = config
    assert actual == expected


def test_that_an_empty_connection_can_be_mapped(blank_config):
    expected = blank_config
    connection = Connection(uri="")
    result = blank_config.from_connection(connection)
    assert result == expected


def test_that_resolve_calls_fill_in_when_env_avail(mock_config):
    """Tests that resolve calls fill in once given a condition"""
    mocked_config = mock_config.config
    mock_config.config.resolve
    mocked_config.is_env_available.assert_called()


def test_that_resolve_does_not_call_fill_in_when_env_not_avail(mock_config):
    """Tests that resolve calls fill in once given a condition"""
    mocked_config = mock_config.config
    mock_config.config.resolve
    mocked_config.is_env_available.assert_called()
    mocked_config.fill_in.assert_not_called()


def test_that_fill_in_fills_na_attr(kwargs, config):
    config_fields = fields(config)
    for config_field in config_fields:
        name = config_field.name
        assert getattr(config, name, None) is not None


def test_that_fill_in_does_nothing_with_non_na_attr(kwargs):
    # TODO
    pass


def test_that_get_connection_from_env_creates_connection_obj(
    mock_connection_env_var, config
):
    assert isinstance(config.__class__.get_connection_from_env(), Connection)


def test_that_is_env_available_returns_true_when_connection_env_var_exists(
    mock_connection_env_var, config
):
    assert config.__class__.is_env_available() is True


def test_that_is_env_available_returns_false_when_connection_env_var_does_not_exist(
    config,
):
    assert config.__class__.is_env_available() is False
