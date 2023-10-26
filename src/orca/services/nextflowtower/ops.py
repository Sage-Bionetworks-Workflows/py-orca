import asyncio
import logging
from dataclasses import field
from functools import cached_property
from typing import ClassVar, Optional

from pydantic.dataclasses import dataclass

from orca.errors import ConfigError
from orca.services.base.ops import BaseOps
from orca.services.nextflowtower.client import NextflowTowerClient
from orca.services.nextflowtower.client_factory import NextflowTowerClientFactory
from orca.services.nextflowtower.config import NextflowTowerConfig
from orca.services.nextflowtower.models import (
    LaunchInfo,
    Workflow,
    WorkflowStatus,
    WorkflowTask,
)
from orca.services.nextflowtower.utils import increment_suffix

logger = logging.getLogger(__name__)


@dataclass(kw_only=False)
class NextflowTowerOps(BaseOps):
    """Collection of operations for Nextflow Tower.

    Attributes:
        config: A configuration object for this service.

    Class Variables:
        client_factory_class: The class for constructing clients.
    """

    config: NextflowTowerConfig = field(default_factory=NextflowTowerConfig)

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
        ignore_previous_runs: bool = False,
    ) -> str:
        """Launch a workflow using the latest matching compute env.

        Args:
            launch_info: Workflow launch information.
            compute_env_filter: Filter for matching compute
                environments. Default to None.
            ignore_previous_runs: Whether to ignore previous
                workflow runs with the same attributes. Note
                that enabling this might result in duplicate
                workflow runs.

        Returns:
            Workflow run ID.
        """
        # Make sure that essential attributes are set
        if launch_info.pipeline is None or launch_info.run_name is None:
            message = "LaunchInfo 'run_name' and 'pipeline' attributes must be set."
            raise ValueError(message)

        # Update launch_info if there are previous workflow runs
        if not ignore_previous_runs:
            latest_run = self.get_latest_previous_workflow(launch_info)
            if latest_run:
                state = latest_run.status.state
                run_repr = f"{latest_run.run_name} (id='{latest_run.id}', {state=})"
                # Return ID for latest run if ongoing, succeeded, or cancelled
                if not latest_run.status.is_done:  # pragma: no cover
                    logger.info(f"Found an ongoing previous run: {run_repr}")
                    return latest_run.id
                if state in {"SUCCEEDED", "UNKNOWN"}:
                    logger.info(f"Found a previous run: {run_repr}")
                    return latest_run.id
                launch_info.fill_in("resume", True)
                launch_info.fill_in("session_id", latest_run.session_id)
                launch_info.run_name = increment_suffix(latest_run.run_name)
                logger.info(f"Relaunching from a previous run: {run_repr}")

        # Get relevant compute environment and its resource tags
        compute_env_id = self.get_latest_compute_env(compute_env_filter)
        compute_env = self.client.get_compute_env(compute_env_id, self.workspace_id)
        label_ids = [label.id for label in compute_env.labels]

        # Ensure that all workflows are labeled for easy querying
        query_label_id = self.create_label(self.launch_label)
        label_ids.append(query_label_id)

        # TODO: Fill in revision using '/pipelines/info' endpoint
        # Update launch_info with compute_env defaults and label ID
        launch_info.fill_in("compute_env_id", compute_env.id)
        launch_info.fill_in("work_dir", compute_env.work_dir)
        launch_info.fill_in("pre_run_script", compute_env.pre_run_script)
        launch_info.add_in("label_ids", label_ids)

        workflow_id = self.client.launch_workflow(launch_info, self.workspace_id)
        workflow_repr = f"{launch_info.run_name} ({workflow_id})"
        logger.info(f"Launched a new workflow run: {workflow_repr}")
        return workflow_id

    def get_workflow(self, workflow_id: str) -> Workflow:
        """Retrieve details about a workflow run.

        Args:
            workflow_id: Workflow run ID.

        Returns:
            Workflow instance.
        """
        return self.client.get_workflow(workflow_id, self.workspace_id)

    def list_workflows(self, search_filter: str = "") -> list[Workflow]:
        """List available workflows that match search filter.

        Attributes:
            search_filter: A Nextflow Tower search query, as you would
                compose it in the runs search bar. Defaults to nothing.
            only_orca_launches: Whether to filter list of workflows for
                those that were launched by Orca. Defaults to True.

        Returns:
            List of workflow instances.
        """
        if self.launch_label is not None:
            search_filter = f"{search_filter} label:{self.launch_label}"
        workflows = self.client.list_workflows(search_filter, self.workspace_id)
        return workflows

    def list_previous_workflows(self, launch_info: LaunchInfo) -> list[Workflow]:
        """Retrieve the list of previously launched workflows.

        Args:
            launch_info: Workflow launch information.

        Returns:
            List of previously launched workflows.
        """
        workflows = self.list_workflows()

        previous_workflows = list()
        for workflow in workflows:
            if workflow.project_name != launch_info.pipeline:
                continue

            # TODO: Rename `run_name` to `unique_id` (or similar)
            prefix = launch_info.run_name
            if prefix and not workflow.run_name.startswith(prefix):
                continue

            previous_workflows.append(workflow)

        return previous_workflows

    def get_latest_previous_workflow(
        self,
        launch_info: LaunchInfo,
    ) -> Optional[Workflow]:
        """Retrieve the latest run among previously launched workflows.

        Args:
            launch_info: Workflow launch information.

        Returns:
            Latest run among previously launched workflows.
        """
        previous_runs = self.list_previous_workflows(launch_info)
        if len(previous_runs) == 0:
            return None

        # First check and return any ongoing runs
        ongoing_runs = [run for run in previous_runs if not run.status.is_done]
        if len(ongoing_runs) > 1:  # pragma: no cover
            message = f"Multiple ongoing workflow runs: {ongoing_runs}"
            raise ValueError(message)
        elif len(ongoing_runs) == 1:
            return ongoing_runs[0]

        # Otherwise, return latest based on submission timestamp
        sorted_runs = sorted(previous_runs, key=lambda x: x.get("submit"))
        return sorted_runs[-1]

    async def monitor_workflow(
        self, run_id: str, wait_time: int = 60 * 5
    ) -> WorkflowStatus:
        """Wait until the workflow run completes.

        Args:
            run_id: Workflow run ID.
            wait_time: Number of seconds to wait between checks.
                Default is 5 minutes.

        Returns:
            Final workflow status.
        """
        workflow = self.get_workflow(run_id)
        while not workflow.status.is_done:
            logger.info(f"{workflow} is not done yet...")
            await asyncio.sleep(wait_time)
            workflow = self.get_workflow(run_id)

        logger.info(f"{workflow} is now done!")
        return workflow.status

    def get_workflow_tasks(self, workflow_id: str) -> list[WorkflowTask]:
        """Retrieve the details of a workflow run's tasks.

        Args:
            workflow_id: Workflow run ID.

        Returns:
            List of task details.
        """
        return self.client.get_workflow_tasks(workflow_id, self.workspace_id)

    def get_task_logs(self, workflow_id: str, task_id: int) -> str:
        """Retrieve the execution logs for a given workflow task.

        Args:
            workflow_id: Workflow run ID.
            task_id: Task ID.

        Returns:
            Task logs.
        """
        return self.client.get_task_logs(workflow_id, task_id, self.workspace_id)
