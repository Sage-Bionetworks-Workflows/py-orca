import pytest

from orca.services.nextflowtower import (
    NextflowTowerClient,
    NextflowTowerConfig,
    NextflowTowerOps,
    models,
)


@pytest.fixture
def config():
    yield NextflowTowerConfig()


@pytest.fixture
def client(config):
    yield NextflowTowerClient(config.auth_token, config.api_endpoint)


@pytest.fixture
def ops(config):
    yield NextflowTowerOps(config)


@pytest.mark.integration
def test_that_the_config_can_pull_information_from_env(config):
    assert config.auth_token
    assert config.api_endpoint


@pytest.mark.integration
def test_that_a_valid_client_can_be_constructed_and_tested(client):
    assert client.list_user_workspaces()


@pytest.mark.integration
def test_that_a_workflow_can_be_launched(ops):
    launch_info = models.LaunchInfo(
        pipeline="nextflow-io/hello",
        run_name="test_launch_workflow",
    )
    workflow_id = ops.launch_workflow(launch_info, "spot", ignore_previous_runs=True)
    assert workflow_id


@pytest.mark.integration
def test_that_a_workflow_can_be_retrieved(ops):
    launch_info = models.LaunchInfo(
        pipeline="nextflow-io/hello",
        run_name="test_get_workflow",
    )
    workflow_id = ops.launch_workflow(launch_info, "spot")
    workflow = ops.get_workflow(workflow_id)
    assert workflow


@pytest.mark.integration
def test_that_a_workflow_can_be_relaunched(ops):
    launch_info = models.LaunchInfo(
        pipeline="nextflow-io/hello",
        run_name="test_relaunch_workflow",
    )
    workflow_id = ops.launch_workflow(launch_info, "spot")
    assert workflow_id
