from functools import cached_property

from pydantic.dataclasses import dataclass

from orca.errors import ConfigError
from orca.services.base.ops import BaseOps
from orca.services.nextflowtower.client_factory import NextflowTowerClientFactory
from orca.services.nextflowtower.config import NextflowTowerConfig


@dataclass(kw_only=False)
class NextflowTowerOps(BaseOps):
    """Collection of operations for Nextflow Tower.

    Attributes:
        config: A configuration object for this service.

    Class Variables:
        client_factory_class: The class for constructing clients.
    """

    config: NextflowTowerConfig

    client_factory_class = NextflowTowerClientFactory

    @cached_property
    def workspace_id(self) -> int:
        """The currently active Nextflow Tower workspace ID."""
        workspaces = self.client.list_user_workspaces()
        for workspace in workspaces:
            full_name = f"{workspace['orgName']}/{workspace['workspaceName']}"
            if full_name.lower() == self.workspace.lower():
                return workspace["workspaceId"]
        message = f"Workspace ({self.workspace}) not available to user ({workspaces})."
        raise ValueError(message)

    @cached_property
    def workspace(self) -> str:
        """The currently active Nextflow Tower workspace name."""
        if self.config.workspace is None:
            message = f"Config ({self.config}) does not specify a workspace."
            raise ConfigError(message)
        return self.config.workspace

    def get_workflow(self, workflow_id: str) -> dict:
        """Gets available information about a workflow run

        Attributes:
            workflow_id (str): The ID number for a workflow run to get information about

        Returns:
            response (dict): Dictionary containing information about the workflow run
        """
        path = f"/workflow/{workflow_id}"
        response = self.client.get(path=path, params={"workspaceId": self.workspace_id})
        return response

    def get_workflow_status(self, workflow_id: str) -> tuple:
        """Gets status of workflow run

        Args:
            workflow_id (str): The ID number for a workflow run to get information about

        Returns:
            tuple: Tuple containing 1. status (str) and 2. Whether the workflow is done (boolean)
        """
        response = self.get_workflow(workflow_id=workflow_id)
        return (
            response["workflow"]["status"],
            bool(response["workflow"]["complete"]),
        )
