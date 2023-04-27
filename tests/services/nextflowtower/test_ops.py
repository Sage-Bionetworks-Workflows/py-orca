import pytest

from orca.errors import ConfigError
from orca.services.nextflowtower import NextflowTowerConfig, NextflowTowerOps


def test_that_the_workspace_attribute_is_accessible(ops):
    assert ops.workspace == "Foo-Bar/project-2"


def test_for_an_error_when_the_workspace_attribute_is_missing(patch_os_environ):
    config = NextflowTowerConfig()
    ops = NextflowTowerOps(config)
    with pytest.raises(ConfigError):
        ops.workspace


def test_that_the_workspace_id_attribute_is_accessible(ops, mocker, get_response):
    response = get_response("get_user_workspaces_and_orgs")
    mock = mocker.patch.object(NextflowTowerOps, "client")
    response = response["orgsAndWorkspaces"]
    mock.list_user_workspaces.return_value = response
    assert ops.workspace_id == 98765


def test_for_error_when_the_workspace_id_does_not_exist(ops, mocker, get_response):
    # Get rid of relevant entry
    response = get_response("get_user_workspaces_and_orgs")
    items = response["orgsAndWorkspaces"]
    items_filtered = [item for item in items if item["workspaceName"] != "project-2"]

    mock = mocker.patch.object(NextflowTowerOps, "client")
    mock.list_user_workspaces.return_value = items_filtered
    with pytest.raises(ValueError):
        ops.workspace_id
