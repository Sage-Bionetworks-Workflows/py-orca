from unittest.mock import MagicMock

import pytest
from airflow.exceptions import AirflowNotFoundException
from airflow.models.connection import Connection
from sevenbridges.api import (
    Actions,
    Api,
    App,
    AsyncJob,
    Automation,
    AutomationPackage,
    AutomationRun,
    BillingGroup,
    Dataset,
    Division,
    DRSImportBulk,
    Endpoints,
    Export,
    File,
    Import,
    Invoice,
    Marker,
    Project,
    RateLimit,
    Task,
    Team,
    User,
    Volume,
)

from orca.services.base.hook import BaseHook
from orca.services.sevenbridges import (
    SevenBridgesConfig,
    SevenBridgesHook,
    SevenBridgesOps,
)


@pytest.fixture
def mock_api(mocker):
    class MockApi(Api):
        """A mocked version of the SevenBridge API.

        This is necessary for getting passed pydantic
        validation of attribute values, such as the
        `client` attribute on SevenBridgesTasks, which
        is supposed to be an instance of Api.
        """

        actions = MagicMock(Actions)
        apps = MagicMock(App)
        async_jobs = MagicMock(AsyncJob)
        automations = MagicMock(Automation)
        automation_runs = MagicMock(AutomationRun)
        automation_packages = MagicMock(AutomationPackage)
        billing_groups = MagicMock(BillingGroup)
        datasets = MagicMock(Dataset)
        divisions = MagicMock(Division)
        drs_imports = MagicMock(DRSImportBulk)
        endpoints = MagicMock(Endpoints)
        exports = MagicMock(Export)
        files = MagicMock(File)
        imports = MagicMock(Import)
        invoices = MagicMock(Invoice)
        markers = MagicMock(Marker)
        projects = MagicMock(Project)
        rate_limit = MagicMock(RateLimit)
        tasks = MagicMock(Task)
        teams = MagicMock(Team)
        users = MagicMock(User)
        volumes = MagicMock(Volume)

    yield mocker.patch("orca.services.sevenbridges.client_factory.Api", MockApi)


@pytest.fixture
def mock_api_init(mock_api, mocker):
    yield mocker.spy(mock_api, "__init__")


@pytest.fixture
def config():
    config = SevenBridgesConfig(
        api_endpoint="https://api.sbgenomics.com/v2",
        auth_token="foo",
        project="bgrande/sandbox",
    )
    yield config


@pytest.fixture
def mock_ops(config, mock_api):
    yield SevenBridgesOps(config)


# Note that this refers to a SevenBridges task (or workflow run)
@pytest.fixture
def mock_task(mocker):
    mock_task = mocker.MagicMock(Task)
    mock_task.id = "123"
    mock_task.name = "foo"
    mock_task.app = "user/bar"
    yield mock_task


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
    yield SevenBridgesHook("foo")
