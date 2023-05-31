import pytest

from orca.services.synapse import SynapseClientFactory, SynapseConfig, SynapseOps


@pytest.fixture
def syn_project_id():
    yield "syn51469029"


@pytest.fixture
def config(patch_os_environ):
    yield SynapseConfig("foo")


@pytest.fixture
def client(config):
    factory = SynapseClientFactory(config=config)
    yield factory.create_client()


@pytest.fixture
def mocked_ops(config, client, mocker):
    mocker.patch.object(SynapseOps, "client", return_value=client)
    yield SynapseOps(config)


@pytest.fixture
def ops(config):
    yield SynapseOps(config)
