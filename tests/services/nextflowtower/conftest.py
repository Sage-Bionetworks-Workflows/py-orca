import pytest
from airflow.exceptions import AirflowNotFoundException
from airflow.models.connection import Connection

from orca.services.base.hook import BaseHook
from orca.services.nextflowtower import (
    NextflowTowerConfig,
    NextflowTowerHook,
    NextflowTowerOps,
)


@pytest.fixture
def mock_client(mocker):
    mocker.patch("orca.services.nextflowtower.client_factory.NextflowTowerClient")


@pytest.fixture
def config():
    config = NextflowTowerConfig(
        api_endpoint="https://api.tower.nf/",
        auth_token="foo",
        workspace=123456789,
    )
    yield config


@pytest.fixture
def mock_ops(config, mock_client):
    yield NextflowTowerOps(config)


@pytest.fixture
def connection_uri(config):
    bare_url = config.api_endpoint.replace("https://", "")
    host, schema = bare_url.rstrip("/").rsplit("/", maxsplit=1)
    token = config.auth_token
    project = config.project
    yield f"sbg://:{token}@{host}/{schema}/?project={project}"


@pytest.fixture
def connection(connection_uri):
    yield Connection(uri=connection_uri)


@pytest.fixture
def patch_get_connection(mocker, connection):
    connection_mock = mocker.patch.object(BaseHook, "get_connection")
    connection_mock.side_effect = AirflowNotFoundException
    yield connection_mock


@pytest.fixture
def hook(patch_get_connection):
    # The conn_id param doesn't matter because the `patch_get_connection`
    # fixture will ensure that the same Connection object is returned
    yield NextflowTowerHook("foo")
