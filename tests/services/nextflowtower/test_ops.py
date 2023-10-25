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
        run_name="foobar",
        revision="1.1",
        profiles=["test"],
        params={"outdir": "foo"},
        work_dir="bar",
    )

    mocker.patch.object(mocked_ops, "get_latest_compute_env")

    response = get_response("get_compute_env")
    mocker.patch.object(mocked_ops.client, "get", return_value=response)

    mocked_ops.launch_workflow(launch_info, "ondemand")
    mocked_ops.client.launch_workflow.assert_called_once()
    assert launch_info.compute_env_id == response["computeEnv"]["id"]


def test_that_list_workflows_filters_on_launch_label(mocked_ops, mocker):
    mock = mocker.patch.object(mocked_ops.client, "list_workflows")
    mocked_ops.list_workflows()
    mock.assert_called_once()
    search_filter = mock.call_args.args[0]
    assert f"label:{mocked_ops.launch_label}" in search_filter


def test_that_list_workflows_doesnt_filter_on_launch_label_when_absent(
    mocked_ops, mocker
):
    mock = mocker.patch.object(mocked_ops.client, "list_workflows")
    mocked_ops.launch_label = None
    mocked_ops.list_workflows()
    mock.assert_called_once()
    search_filter = mock.call_args.args[0]
    assert f"label:{mocked_ops.launch_label}" not in search_filter


def test_that_list_previous_workflows_matches_the_right_entries(
    mocked_ops, client, mocker, get_response
):
    mock = mocker.patch.object(client, "get")
    mock.return_value = get_response("list_workflows")
    workflows = client.list_workflows()

    launch_info = models.LaunchInfo(
        pipeline="nf-core/rnaseq",
        revision="3.11.2",
        profiles=["test"],
        run_name="hungry_cori",
        params={"outdir": "foo"},
    )
    mocker.patch.object(mocked_ops, "list_workflows", return_value=workflows)
    result = mocked_ops.list_previous_workflows(launch_info)
    assert len(result) == 2


def test_that_get_latest_previous_workflow_returns_an_ongoing_run(
    mocked_ops, client, mocker, get_response
):
    mock = mocker.patch.object(client, "get")
    mock.return_value = get_response("get_workflow")
    workflow = client.get_workflow("foo")
    workflow.state = models.WorkflowState("RUNNING")

    launch_info = models.LaunchInfo(
        pipeline="nf-core/rnaseq",
        revision="3.11.2",
        profiles=["test"],
        run_name="hungry_cori",
        params={"outdir": "foo"},
    )
    mocker.patch.object(mocked_ops, "list_previous_workflows", return_value=[workflow])
    result = mocked_ops.get_latest_previous_workflow(launch_info)
    assert result.id == workflow.id


def test_for_an_error_when_launching_a_workflow_without_a_run_name(mocked_ops):
    launch_info = models.LaunchInfo(pipeline="nf-core/rnaseq")
    with pytest.raises(ValueError):
        mocked_ops.launch_workflow(launch_info)


def test_for_an_error_when_launching_a_workflow_without_a_pipeline(mocked_ops):
    launch_info = models.LaunchInfo(run_name="foobar")
    with pytest.raises(ValueError):
        mocked_ops.launch_workflow(launch_info)


def test_that_launch_workflow_considers_previous_runs(
    mocked_ops, client, mocker, get_response
):
    wf_mock = mocker.patch.object(client, "get")
    wf_mock.return_value = get_response("get_workflow")
    workflow = client.get_workflow("foo")
    workflow.state = models.WorkflowState("FAILED")

    latest_wf_mock = mocker.patch.object(mocked_ops, "get_latest_previous_workflow")
    latest_wf_mock.return_value = workflow

    mocker.patch.object(mocked_ops, "get_latest_compute_env")

    latest_ce_mock = mocker.patch.object(client, "get")
    latest_ce_mock.return_value = get_response("get_compute_env")
    compute_env = client.get_compute_env("foo")
    mocker.patch.object(mocked_ops.client, "get_compute_env", return_value=compute_env)

    mocker.patch.object(mocked_ops, "create_label", return_value=123)

    launch_info = models.LaunchInfo(
        pipeline="nextflow-io/example-workflow",
        run_name="example-run",
    )

    launch_mock = mocker.patch.object(mocked_ops.client, "launch_workflow")
    mocked_ops.launch_workflow(launch_info)

    launch_mock.assert_called_once()
    assert launch_info.run_name == "example-run_2"
    assert launch_info.resume
    assert launch_info.session_id == workflow.session_id


def test_that_launch_workflow_works_when_there_are_no_previous_runs(
    mocked_ops, client, mocker, get_response
):
    latest_wf_mock = mocker.patch.object(mocked_ops, "get_latest_previous_workflow")
    latest_wf_mock.return_value = None

    mocker.patch.object(mocked_ops, "get_latest_compute_env")

    latest_ce_mock = mocker.patch.object(client, "get")
    latest_ce_mock.return_value = get_response("get_compute_env")
    compute_env = client.get_compute_env("foo")
    mocker.patch.object(mocked_ops.client, "get_compute_env", return_value=compute_env)

    mocker.patch.object(mocked_ops, "create_label", return_value=123)

    launch_info = models.LaunchInfo(
        pipeline="nextflow-io/example-workflow",
        run_name="example-run",
    )

    launch_mock = mocker.patch.object(mocked_ops.client, "launch_workflow")
    mocked_ops.launch_workflow(launch_info)

    launch_mock.assert_called_once()
    assert launch_info.run_name == "example-run"
    assert not launch_info.resume
    assert launch_info.session_id is None


@pytest.mark.asyncio
async def test_that_monitor_workflow_works_for_a_complete_workflow(
    mocker, get_response, mocked_ops
):
    response = get_response("get_workflow")
    workflow = models.Workflow.from_json(response["workflow"])

    mock = mocker.patch.object(mocked_ops, "get_workflow")
    mock.return_value = workflow

    result = await mocked_ops.monitor_workflow("123456789", wait_time=0.01)

    mock.assert_called_once()
    assert result == models.WorkflowStatus("SUCCEEDED")


@pytest.mark.asyncio
async def test_that_monitor_workflow_works_for_an_incomplete_workflow(
    mocker, get_response, mocked_ops
):
    response = get_response("get_workflow")
    complete_workflow = models.Workflow.from_json(response["workflow"])
    incomplete_workflow = replace(complete_workflow, state="RUNNING")

    mock = mocker.patch.object(mocked_ops, "get_workflow")
    mock.side_effect = [incomplete_workflow] * 2 + [complete_workflow]

    result = await mocked_ops.monitor_workflow("123456789", wait_time=0.01)

    assert mock.call_count > 1
    assert result == models.WorkflowStatus("SUCCEEDED")


def test_that_get_workflow_tasks_works(mocked_ops, mocker, get_response, client):
    response = get_response("get_workflow_tasks")
    expected = [
        models.WorkflowTask.from_json(task["task"]) for task in response["tasks"]
    ]
    mock = mocker.patch.object(mocked_ops.client, "get_workflow_tasks")
    mock.return_value = expected
    result = mocked_ops.get_workflow_tasks(workflow_id="123456789")
    mock.assert_called()
    assert expected == result


def test_that_get_task_logs_works(mocked_ops, mocker, get_response):
    expected = "Ciao world!"
    mock = mocker.patch.object(mocked_ops.client, "get_task_logs")
    mock.return_value = expected
    result = mocked_ops.get_task_logs(task_id=1, workflow_id="123456789")
    mock.assert_called()
    assert result == "Ciao world!"
