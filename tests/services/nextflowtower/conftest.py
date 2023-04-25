import pytest

from orca.services.nextflowtower import (
    NextflowTowerClient,
    NextflowTowerConfig,
    NextflowTowerOps,
)


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
