import pytest
from airflow.models.connection import Connection

from orca.services.nextflowtower import NextflowTowerConfig, NextflowTowerHook
from orca.services.sevenbridges import SevenBridgesConfig, SevenBridgesHook

SUBCLASSES = {
    SevenBridgesHook: {
        "api_endpoint": "https://api.sbgenomics.com/v2",
        "auth_token": "foo",
        "project": "bgrande/sandbox",
    },
    NextflowTowerHook: {
        "api_endpoint": "https://tower-dev.sagebionetworks.org/api",
        "auth_token": "foo",
        "workspace": "sage-bionetworks/example-project",
    },
}

SUBCLASS_CONFIG_QUERY_KEYS = {
    SevenBridgesConfig: "project",
    NextflowTowerConfig: "workspace",
}


@pytest.fixture(
    params=SUBCLASSES.items(), ids=[subclass.__name__ for subclass in SUBCLASSES]
)
def ops(request):
    hook_cls, params = request.param
    config = hook_cls.config_class(**params)
    ops = hook_cls.ops_class(config)
    yield ops


@pytest.fixture()
def client_factory(ops):
    yield ops.client_factory_class(ops.config)


@pytest.fixture(params=SUBCLASSES.keys())
def blank_client_factory(request):
    hook_cls = request.param
    config = hook_cls.config_class()
    ops = hook_cls.ops_class(config)
    yield ops.client_factory_class(config)


@pytest.fixture()
def client_class(ops):
    yield ops.client_factory_class(ops.config).client_class


@pytest.fixture()
def config(ops):
    yield ops.config


@pytest.fixture
def connection_uri(config):
    bare_url = config.api_endpoint.replace("https://", "")
    host, schema = bare_url.rstrip("/").rsplit("/", maxsplit=1)
    token = config.auth_token
    query_key = SUBCLASS_CONFIG_QUERY_KEYS[config.__class__]
    query_val = getattr(config, query_key)
    yield f"sbg://:{token}@{host}/{schema}/?{query_key}={query_val}"


@pytest.fixture
def connection(connection_uri):
    yield Connection(uri=connection_uri)


@pytest.fixture(params=SUBCLASSES.keys())
def blank_config(request):
    hook_cls = request.param
    config = hook_cls.config_class()
    ops = hook_cls.ops_class(config)
    yield ops.config


@pytest.fixture
def patched_ops(mocker, ops):
    mock_client_factory = mocker.MagicMock(ops.client_factory_class)
    mocker.patch.object(ops, "client_factory_class", mock_client_factory)
    yield ops


@pytest.fixture
def mock_config(mocker, ops):
    mock_config = mocker.MagicMock(ops.config)
    mocker.patch.object(ops, "config", mock_config)
    yield ops


@pytest.fixture
def mock_connection_env_var(monkeypatch, config):
    monkeypatch.setenv(config.connection_env_var, "some_value")
