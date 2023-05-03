from copy import deepcopy

import pytest

from orca.services.nextflowtower import (
    NextflowTowerClient,
    NextflowTowerConfig,
    NextflowTowerOps,
)

from . import responses


@pytest.fixture
def client(patch_os_environ):
    yield NextflowTowerClient("foo", "bar")


@pytest.fixture
def config(patch_os_environ):
    # Workspace name based on example in responses.py
    yield NextflowTowerConfig("foo", "bar", "Foo-Bar/project-2")


@pytest.fixture
def ops(config):
    yield NextflowTowerOps(config)


# TODO: Mock `client` using a property mock
@pytest.fixture
def mocked_ops(config, client, mocker):
    mocker.patch.object(NextflowTowerOps, "client", return_value=client)
    mocker.patch.object(NextflowTowerOps, "workspace_id", return_value=98765)
    yield NextflowTowerOps(config)


@pytest.fixture(scope="session")
def get_response():
    def _get_response(name: str) -> dict:
        response = getattr(responses, name)
        return deepcopy(response)

    yield _get_response
