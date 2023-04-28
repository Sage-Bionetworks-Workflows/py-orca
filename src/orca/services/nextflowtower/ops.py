from functools import cached_property
from typing import Optional

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

    def get_latest_compute_env(self, filter: Optional[str] = None) -> str:
        """Get latest available compute environment matching filter.

        Args:
            filter: A string to filter compute environment names.
                For example, "ondemand" for filtering for on-demand
                compute environments. Default to None, which doesn't
                apply any filtering.

        Raises:
            ValueError: If no matching compute environments exist.

        Returns:
            Compute environment ID.
        """
        envs = self.client.list_compute_envs(self.workspace_id, "AVAILABLE")
        if filter:
            envs = [env for env in envs if filter in env["name"]]
        if len(envs) == 0:
            message = f"No matching compute environments ({filter=})."
            raise ValueError(message)
        elif len(envs) == 1:
            return envs[0]["id"]

        # Sort by dateCreated if there are multiple matches
        envs_info = list()
        for env in envs:
            info = self.client.get_compute_env(env["id"], self.workspace_id)
            envs_info.append(info)

        envs_info = sorted(envs_info, key=lambda x: x["dateCreated"])
        latest_env = envs_info[-1]
        return latest_env["id"]
