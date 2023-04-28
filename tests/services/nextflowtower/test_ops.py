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


def test_that_get_workflow_returns_expected_response(mocked_ops, ops, get_response):
    response = get_response("get_workflow_complete")
    mocked_ops.client.get.return_value = response
    assert ops.get_workflow(workflow_id="123456789") == response


def test_that_get_workflow_status_returns_expected_tuple_workflow_is_complete(
    ops, mocker, get_response
):
    response = get_response("get_workflow_complete")
    mock = mocker.patch.object(ops, "get_workflow")
    mock.return_value = response
    result = ops.get_workflow_status(workflow_id="123456789")
    assert result == ("SUCCEEDED", True)


def test_that_get_workflow_status_returns_expected_tuple_workflow_is_not_complete(
    ops, mocker, get_response
):
    response = get_response("get_workflow_incomplete")
    mock = mocker.patch.object(ops, "get_workflow")
    mock.return_value = response
    result = ops.get_workflow_status(workflow_id="123456789")
    assert result == ("SUBMITTED", False)
