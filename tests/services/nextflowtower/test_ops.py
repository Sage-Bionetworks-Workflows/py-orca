from dataclasses import replace

import pytest

from orca.errors import ConfigError
from orca.services.nextflowtower import NextflowTowerConfig, NextflowTowerOps, models
from orca.services.nextflowtower.utils import parse_datetime


def test_that_the_workspace_attribute_is_accessible(ops):
    assert ops.workspace == "foo-bar/project-2"


def test_for_an_error_when_the_workspace_attribute_is_missing(patch_os_environ):
    config = NextflowTowerConfig()
    ops = NextflowTowerOps(config)
    with pytest.raises(ConfigError):
        ops.workspace


def test_that_the_workspace_id_attribute_is_accessible(
    client, config, mocker, get_response
):
    response = get_response("get_user_workspaces_and_orgs")["orgsAndWorkspaces"]
    workspaces_json = [item for item in response if item["workspaceId"]]
    workspaces = [models.Workspace.from_json(item) for item in workspaces_json]

    mock = mocker.patch.object(NextflowTowerOps, "client", return_value=client)
    mock.list_user_workspaces.return_value = workspaces

    config.workspace = "foo-bar/project-1"
    ops = NextflowTowerOps(config)
    assert ops.workspace_id == 54321


def test_for_error_when_the_workspace_id_does_not_exist(
    client, config, mocker, get_response
):
    response = get_response("get_user_workspaces_and_orgs")["orgsAndWorkspaces"]
    workspaces_json = [item for item in response if item["workspaceId"]]
    workspaces = [models.Workspace.from_json(item) for item in workspaces_json]

    mock = mocker.patch.object(NextflowTowerOps, "client", return_value=client)
    mock.list_user_workspaces.return_value = workspaces

    config.workspace = "foo-bar/project-3"
    ops = NextflowTowerOps(config)
    with pytest.raises(ValueError):
        ops.workspace_id


def test_that_get_latest_compute_env_handles_multiple_envs(mocked_ops, get_response):
    # Patch list_compute_envs() to return a list of ComputeEnvSummary objects
    # This should result in two matching compute environments
    response = get_response("list_compute_envs")
    summaries = map(models.ComputeEnvSummary.from_json, response["computeEnvs"])
    mocked_ops.client.list_compute_envs.return_value = list(summaries)

    # Create function for generating compute environments
    def generate_compute_env(id, date):
        compute_env_response = get_response("get_compute_env")["computeEnv"]
        compute_env = models.ComputeEnv.from_json(compute_env_response)
        return replace(compute_env, id=id, date_created=parse_datetime(date))

    # Generate full compute environments
    mocked_ops.client.get_compute_env.side_effect = [
        generate_compute_env("5ykJF", "2023-04-26T00:49:49Z"),
        generate_compute_env("9W2l7", "2023-01-11T13:32:54Z"),
    ]

    result = mocked_ops.get_latest_compute_env("ondemand")
    assert result == "5ykJF"


def test_that_get_latest_compute_env_handles_single_env(mocked_ops, get_response):
    # Patch list_compute_envs() to return a list of ComputeEnvSummary objects
    # This should result in one matching compute environment
    response = get_response("list_compute_envs")
    del response["computeEnvs"][2]
    summaries = map(models.ComputeEnvSummary.from_json, response["computeEnvs"])
    mocked_ops.client.list_compute_envs.return_value = list(summaries)

    result = mocked_ops.get_latest_compute_env("ondemand")
    assert result == "5ykJF"


def test_for_an_error_when_get_latest_compute_env_finds_no_env(mocked_ops):
    mocked_ops.client.list_compute_envs.return_value = list()
    with pytest.raises(ValueError):
        mocked_ops.get_latest_compute_env()


def test_that_create_label_doesnt_create_duplicates(mocked_ops, get_response):
    labels_json = get_response("list_labels")["labels"]
    labels = [models.Label.from_json(item) for item in labels_json]
    mocked_ops.client.list_labels.return_value = labels

    mocked_ops.create_label("launched-by-orca")
    mocked_ops.client.create_label.assert_not_called()


def test_that_create_label_creates_missing_labels(mocked_ops, get_response):
    labels_json = get_response("list_labels")["labels"]
    labels = [models.Label.from_json(item) for item in labels_json]
    mocked_ops.client.list_labels.return_value = labels

    mocked_ops.create_label("something-missing")
    mocked_ops.client.create_label.assert_called_once()


def test_that_create_label_ignores_resource_labels(mocked_ops, get_response):
    labels_json = get_response("list_labels")["labels"]
    labels = [models.Label.from_json(item) for item in labels_json]
    mocked_ops.client.list_labels.return_value = labels

    mocked_ops.create_label("CostCenter")  # Existing resource label
    mocked_ops.client.create_label.assert_called_once()


def test_that_launch_workflow_works(mocked_ops, get_response, mocker):
    launch_info = models.LaunchInfo(
        compute_env_id="5ykJF",
        pipeline="some/pipeline",
        revision="1.1",
        profiles=["test"],
        params={"outdir": "foo"},
        work_dir="bar",
    )

    mocker.patch.object(mocked_ops, "get_latest_compute_env")

    compute_env_response = get_response("get_compute_env")["computeEnv"]
    compute_env = models.ComputeEnv.from_json(compute_env_response)
    mocked_ops.client.get_compute_env.return_value = compute_env

    mocked_ops.launch_workflow(launch_info, "ondemand")
    mocked_ops.client.launch_workflow.assert_called_once()
    assert launch_info.compute_env_id == compute_env.id


def test_that_get_workflow_status_returns_expected_tuple_workflow_is_complete(
    mocker, get_response, mocked_ops
):
    response = get_response("get_workflow")
    mock = mocker.patch.object(mocked_ops, "client")
    mock.get_workflow.return_value = response
    result = mocked_ops.get_workflow_status(workflow_id="123456789")
    mock.get_workflow.assert_called_once()
    assert result == ("SUCCEEDED", True)


def test_that_get_workflow_status_returns_expected_tuple_workflow_is_not_complete(
    mocked_ops, mocker, get_response
):
    response = get_response("get_workflow")
    response["workflow"]["complete"] = None
    response["workflow"]["status"] = "SUBMITTED"
    mock = mocker.patch.object(mocked_ops, "client")
    mock.get_workflow.return_value = response
    result = mocked_ops.get_workflow_status(workflow_id="123456789")
    mock.get_workflow.assert_called_once()
    assert result == ("SUBMITTED", False)
