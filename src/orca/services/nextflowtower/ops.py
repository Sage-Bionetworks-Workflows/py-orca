from functools import cached_property
from typing import ClassVar, Optional, cast

from pydantic.dataclasses import dataclass

from orca.errors import ConfigError
from orca.services.base.ops import BaseOps
from orca.services.nextflowtower.client import NextflowTowerClient
from orca.services.nextflowtower.client_factory import NextflowTowerClientFactory
from orca.services.nextflowtower.config import NextflowTowerConfig
from orca.services.nextflowtower.models import LaunchInfo, TaskStatus


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

    client: ClassVar[NextflowTowerClient]

    launch_label: ClassVar[str] = "launched-by-orca"

    @cached_property
    def workspace_id(self) -> int:
        """The currently active Nextflow Tower workspace ID."""
        workspaces = self.client.list_user_workspaces()
        for workspace in workspaces:
            if workspace.full_name == self.workspace:
                return workspace.id
        message = f"Workspace ({self.workspace}) not available to user ({workspaces})."
        raise ValueError(message)

    @cached_property
    def workspace(self) -> str:
        """The currently active Nextflow Tower workspace name."""
        if self.config.workspace is None:
            message = f"Config ({self.config}) does not specify a workspace."
            raise ConfigError(message)
        return self.config.workspace.lower()

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
            envs = [env for env in envs if filter in env.name]
        if len(envs) == 0:
            message = f"No matching compute environments ({filter=})."
            raise ValueError(message)
        elif len(envs) == 1:
            return envs[0].id

        # Fill in additional info and sort by dateCreated if there are multiple matches)
        all_details = list()
        for env in envs:
            details = self.client.get_compute_env(env.id, self.workspace_id)
            all_details.append(details)
        all_details = sorted(all_details, key=lambda x: x.date_created)
        latest_env = all_details[-1]
        return latest_env.id

    def create_label(self, name: str) -> int:
        """Create (or get existing) workflow (non-resource) label.

        Args:
            name: Label name.

        Returns:
            Label ID.
        """
        labels = self.client.list_labels(self.workspace_id)
        for label in labels:
            if label.resource:
                continue
            if label.name == name:
                return label.id
        label = self.client.create_label(name, self.workspace_id)
        return label.id

    # TODO: Once get_workflow() is available, try to make idempotent
    def launch_workflow(
        self,
        launch_info: LaunchInfo,
        compute_env_filter: Optional[str] = None,
    ) -> str:
        """Launch a workflow using the latest matching compute env.

        Args:
            launch_info: Workflow launch information.
            compute_env_filter: Filter for matching compute
                environments. Default to None.

        Returns:
            Workflow run ID.
        """
        compute_env_id = self.get_latest_compute_env(compute_env_filter)
        compute_env = self.client.get_compute_env(compute_env_id, self.workspace_id)
        label_ids = [label.id for label in compute_env.labels]

        # Ensure that all workflows are labeled for easy querying
        query_label_id = self.create_label(self.launch_label)
        label_ids.append(query_label_id)

        # Update launch_info with compute_env defaults and label ID
        launch_info.fill_in("compute_env_id", compute_env_id)
        launch_info.fill_in("work_dir", compute_env.work_dir)
        launch_info.fill_in("pre_run_script", compute_env.pre_run_script)
        launch_info.fill_in("label_ids", label_ids)

        return self.client.launch_workflow(launch_info, self.workspace_id)

    def get_workflow_status(self, workflow_id: str) -> tuple[TaskStatus, bool]:
        """Gets status of workflow run

        Args:
            workflow_id (str): The ID number for a workflow run to get information about

        Returns:
            tuple: Tuple containing 1. status (str) and
            2. Whether the workflow is done (boolean)
        """
        response = self.client.get_workflow(
            workspace_id=self.workspace_id, workflow_id=workflow_id
        )
        task_status = cast(TaskStatus, response["workflow"]["status"])
        is_done = task_status in TaskStatus.terminal_states.value
        # TODO: Consider switching return value to a namedtuple
        return task_status, is_done
