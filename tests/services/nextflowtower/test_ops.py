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


def test_that_get_latest_compute_env_handles_multiple_envs(mocked_ops, get_response):
    response = get_response("list_compute_envs")
    mocked_ops.client.list_compute_envs.return_value = response["computeEnvs"]

    # First date is the latest one, matching the response
    mocked_ops.client.get_compute_env.side_effect = [
        {"id": "5ykJF", "dateCreated": "2023-04-26T00:49:49Z"},
        {"id": "9W2l7", "dateCreated": "2023-01-11T13:32:54Z"},
    ]

    result = mocked_ops.get_latest_compute_env("ondemand")
    assert result == "5ykJF"


def test_that_get_latest_compute_env_handles_single_env(mocked_ops, get_response):
    response = get_response("list_compute_envs")
    del response["computeEnvs"][2]
    mocked_ops.client.list_compute_envs.return_value = response["computeEnvs"]

    result = mocked_ops.get_latest_compute_env("ondemand")
    assert result == "5ykJF"


def test_for_an_error_when_get_latest_compute_env_finds_no_env(mocked_ops):
    mocked_ops.client.list_compute_envs.return_value = list()
    with pytest.raises(ValueError):
        mocked_ops.get_latest_compute_env()
