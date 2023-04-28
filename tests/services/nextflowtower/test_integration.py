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


@pytest.mark.cost
@pytest.mark.integration
def test_that_a_workflow_can_be_launched(ops):
    scratch_bucket = "s3://orca-service-test-project-tower-scratch/"
    launch_info = models.LaunchInfo(
        compute_env_id="5ykJFs33AE3d3AgThavz3b",
        pipeline="nf-core/rnaseq",
        revision="3.11.2",
        profiles=["test"],
        params={"outdir": f"{scratch_bucket}/2days/launch_test"},
        work_dir=f"{scratch_bucket}/work",
    )
    workflow_id = ops.launch_workflow(launch_info, "ondemand")
    assert workflow_id
