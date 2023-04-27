import pytest
from airflow.models.connection import Connection

from orca.services.nextflowtower import NextflowTowerConfig


def test_for_validation_error_when_setting_workspace_without_org():
    bad_input = "some-workspace"
    with pytest.raises(ValueError):
        NextflowTowerConfig("foo", "bar", bad_input)


def test_that_config_can_be_configured_with_full_org_workspace_name(patch_os_environ):
    good_input = "some-org/some-workspace"
    assert NextflowTowerConfig("foo", "bar", good_input)


def test_that_parse_connection_can_process_connection_without_host():
    connection = Connection(password="foo")
    kwargs = NextflowTowerConfig.parse_connection(connection)
    assert kwargs["auth_token"] == "foo"
    assert kwargs["api_endpoint"] is None
