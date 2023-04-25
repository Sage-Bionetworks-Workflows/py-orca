import pytest

from orca.errors import ConfigError
from orca.services.nextflowtower import NextflowTowerConfig, NextflowTowerOps

from . import responses


def test_that_the_workspace_attribute_is_accessible(ops):
    assert ops.workspace == "Foo-Bar/project-2"


def test_for_an_error_when_the_workspace_attribute_is_missing(patch_os_environ):
    config = NextflowTowerConfig()
    ops = NextflowTowerOps(config)
    with pytest.raises(ConfigError):
        ops.workspace


def test_that_the_workspace_id_attribute_is_accessible(ops, mocker):
    mock = mocker.patch.object(NextflowTowerOps, "client")
    response = responses.get_user_workspaces_and_orgs["orgsAndWorkspaces"]
    mock.list_user_workspaces.return_value = response
    assert ops.workspace_id == 98765


def test_for_error_when_the_workspace_id_does_not_exist(ops, mocker):
    mock = mocker.patch.object(NextflowTowerOps, "client")
    response = responses.get_user_workspaces_and_orgs["orgsAndWorkspaces"]
    # Get rid of relevant entry
    response = [item for item in response if item["workspaceName"] != "project-2"]
    mock.list_user_workspaces.return_value = response
    with pytest.raises(ValueError):
        ops.workspace_id
