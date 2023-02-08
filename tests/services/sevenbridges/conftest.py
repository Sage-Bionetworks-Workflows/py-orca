from copy import copy

import pytest
from airflow.models.connection import Connection

from orca.services.sevenbridges import client_factory
from orca.services.sevenbridges.hook import SevenBridgesHook


@pytest.fixture
def api_mock(mocker):
    yield mocker.patch.object(client_factory, "Api", autospec=True)


@pytest.fixture
def client_creds():
    client_creds = {
        "api_endpoint": "https://api.sbgenomics.com/v2",
        "auth_token": "foo",
    }
    yield client_creds


@pytest.fixture
def tasks_args(client_creds):
    tasks_args = copy(client_creds)
    tasks_args["project"] = "bgrande/sandbox"
    yield tasks_args


@pytest.fixture
def connection_uri(tasks_args):
    bare_url = tasks_args["api_endpoint"].replace("https://", "")
    host, schema = bare_url.rstrip("/").rsplit("/", maxsplit=1)
    token = tasks_args["auth_token"]
    project = tasks_args["project"]
    yield f"sbg://:{token}@{host}/{schema}/?project={project}"


@pytest.fixture
def connection(connection_uri):
    yield Connection(uri=connection_uri)


@pytest.fixture
def patch_get_connection(mocker, connection):
    connection_mock = mocker.patch.object(SevenBridgesHook, "get_connection")
    connection_mock.return_value = connection
    yield


@pytest.fixture
def hook(patch_get_connection):
    # The conn_id param doesn't matter because the `patch_get_connection`
    # fixture will ensure that the same Connection object is returned
    yield SevenBridgesHook("foo")
