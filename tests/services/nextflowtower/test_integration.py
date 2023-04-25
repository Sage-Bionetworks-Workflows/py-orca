import pytest

from orca.services.nextflowtower import NextflowTowerClient, NextflowTowerConfig


@pytest.mark.integration
def test_that_a_valid_client_can_be_constructed_and_tested():
    config = NextflowTowerConfig()
    assert config.auth_token
    assert config.api_endpoint
    client = NextflowTowerClient(config.auth_token, config.api_endpoint)
    assert client.list_user_workspaces()
