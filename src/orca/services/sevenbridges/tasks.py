from __future__ import annotations

from functools import wraps
from typing import Any, Optional, cast

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from sevenbridges import Api
from sevenbridges.models.enums import TaskStatus

from orca.errors import OptionalAttrRequiredError, UnexpectedMatch
from orca.services.sevenbridges.client_factory import SevenBridgesClientFactory


def project_required(method):
    """Raise error if project is unset when calling method.

    Args:
        method: A SevenBridgesTasks method.

    Returns:
        A modified method that checks that the project attribute
        is set before running the method.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.project is None:
            name = method.__name__
            message = f"`project` attribute must be set before calling `{name}()`."
            raise OptionalAttrRequiredError(message)
        return method(self, *args, **kwargs)

    return wrapper


# TODO: Should I change the class suffix to "Ops" to avoid confusion
#       with the concept of tasks in SevenBridges?
@dataclass
class SevenBridgesTasks:
    """Common tasks for SevenBridges platforms.

    Note that SevenBridges uses the term "tasks" to refer to
    workflow runs. On the other hand, the "tasks" alluded to
    in this class name refer to operations in general.

    Attributes:
        client: An authenticated SevenBridges client.
        project: A SevenBridges project (prefixed by username).
    """

    client: Api
    project: Optional[str] = None

    @classmethod
    def from_creds(
        cls,
        api_endpoint: str,
        auth_token: str,
        project: Optional[str] = None,
        **client_kwargs: Any,
    ) -> SevenBridgesTasks:
        """Construct SevenBridgesTasks from credentials.

        Args:
            api_endpoint: API base endpoint.
            auth_token: An authentication token. Available under the
                Developer menu.
            project: An owner-prefixed SevenBridges project.
                For example: <username>/<project-name>.
                Defaults to None.
            **client_kwargs: Additional keyword arguments that are passed
                to the SevenBridges client during its construction.

        Returns:
            An authenticated SevenBridgesTasks instance.
        """
        factory = SevenBridgesClientFactory(api_endpoint, auth_token, client_kwargs)
        client = factory.get_client()
        return SevenBridgesTasks(client, project)

    @project_required
    def get_task(self, name: str, app_id: str) -> Optional[str]:
        """Retrieve a task ID based on some filters.

        Args:
            name: Task name.
            app_id: App ID.

        Raises:
            UnexpectedMatch: If a task with the given name was found
                but doesn't match the given app ID.

        Returns:
            The matching task ID or `None` if no matches were found.
        """
        project_matches = self.client.tasks.query(project=self.project)
        name_matches = [task for task in project_matches if task.name == name]

        if len(name_matches) == 0:
            return None
        elif len(name_matches) > 1:
            message = f"Found many tasks ({name_matches}) with given name ({name})."
            raise UnexpectedMatch(message)
        else:
            task = name_matches[0]

        if app_id not in task.app:
            message = (
                f"Found task ({task.id}) with given name ({name}), but its app "
                f"({task.app}) doesn't match what's expected ({app_id})."
            )
            raise UnexpectedMatch(message)

        return task.id

    @project_required
    def draft_task(self, name: str, app_id: str, inputs: dict[str, Any]) -> str:
        """Draft a task (workflow run) if need be.

        This method will first query for a task with the given name.

        Args:
            name: Task name.
            app_id: ID of the app used to draft the task.
            inputs: Input parameters for the app.

        Returns:
            The drafted task ID.
        """
        # Make sure that a task doesn't already exist with that name
        matching_task = self.get_task(name, app_id)
        if matching_task is not None:
            return matching_task

        # Note that `create()` does not launch by default (run=False)
        task = self.client.tasks.create(name, self.project, app_id, inputs=inputs)
        task.id = cast(str, task.id)
        return task.id

    def launch_task(self, task_id: str) -> str:
        """Launch a draft task (workflow run).

        Args:
            task_id: Task ID.

        Returns:
            The input task ID (passed through).
        """
        task = self.client.tasks.get(task_id)
        task.run()
        return task_id

    def create_task(self, name: str, app_id: str, inputs: dict[str, Any]) -> str:
        """Draft and launch a task (workflow run).

        Args:
            name: Task name.
            app_id: ID of the app used to draft the task.
            inputs: Input parameters for the app.

        Returns:
            The launched task ID.
        """
        task_id = self.draft_task(name, app_id, inputs)
        return self.launch_task(task_id)

    def get_task_status(self, task_id) -> tuple[TaskStatus, bool]:
        """Retrieve the status of a task and whether it's done.

        Args:
            task_id: Task ID.

        Returns:
            The task status and whether it's done.
        """
        task = self.client.tasks.get(task_id)
        task.status = cast(TaskStatus, task.status)
        is_done = task.status in TaskStatus.terminal_states
        return task.status, is_done
