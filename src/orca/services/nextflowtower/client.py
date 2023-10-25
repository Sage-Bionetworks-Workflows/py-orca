from typing import Any, Optional

import requests
from pydantic.dataclasses import dataclass
from requests.exceptions import HTTPError

from orca.services.nextflowtower import models


@dataclass(kw_only=False)
class NextflowTowerClient:
    """Simple Python client for making requests to Nextflow Tower.

    Attributes:
        api_endpoint: API endpoint for a Nextflow Tower platform.
        auth_token: An authentication token for the platform specified
            by the ``api_endpoints`` value.
    """

    auth_token: str
    api_endpoint: str

    @staticmethod
    def update_kwarg(
        kwargs: dict[str, Any], key1: str, key2: str, default: Any
    ) -> None:
        """Ensure a default value for a nested key in kwargs.

        Args:
            kwargs: Keyword arguments
            key1: Top-level key.
            key2: Nested key.
            default: Default value.

        Raises:
            ValueError: If 'params' isn't a dictionary.
            ValueError: If the existing value under the provided keys
                does not match the type of the default value.
        """
        kwargs.setdefault(key1, dict())
        if not isinstance(kwargs[key1], dict):
            message = f"The '{key1}' keyword argument must be a dictionary."
            raise ValueError(message)
        kwargs[key1].setdefault(key2, default)
        if not isinstance(kwargs[key1][key2], type(default)):
            message = (
                f"The value for kwargs['{key1}']['{key2}'] ({kwargs[key1][key2]}) "
                f"is not the expected type ({type(default)})."
            )
            raise ValueError(message)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an authenticated HTTP request.

        Args:
            method: An HTTP method (GET, PUT, POST, or DELETE).
            path: The API path with the parameters filled in.
            **kwargs: Additional named arguments passed through to
                requests.request().

        Raises:
            ValueError: If the provided method isn't valid.

        Returns:
            The raw Response object to allow for special handling
        """
        url = f"{self.api_endpoint}/{path}"

        auth_header = f"Bearer {self.auth_token}"
        self.update_kwarg(kwargs, "headers", "Authorization", auth_header)

        return requests.request(method, url, **kwargs)

    def request_json(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Make an auth'ed HTTP request and parse the JSON response.

        See ``TowerClient.request`` for argument definitions.

        Raises:
            HTTPError: If something went wrong with the request.

        Returns:
            A dictionary from deserializing the JSON response.
        """
        response = self.request(method, path, **kwargs)
        try:
            response.raise_for_status()
        except HTTPError as e:
            # Add extra context if possible
            raise HTTPError(response.text) from e
        return response.json()

    def request_paged(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Iterate through pages of results for a given request.

        See ``TowerClient.request`` for argument definitions.

        Raises:
            HTTPError: If the response doesn't match the expectation
                for a paged endpoint.

        Returns:
            The cumulative list of items from all pages.
        """
        # Ensure defaults for pagination query parameters
        self.update_kwarg(kwargs, "params", "max", 50)
        self.update_kwarg(kwargs, "params", "offset", 0)

        num_items = 0
        all_items = list()
        key_name = "items"  # Setting a default value
        total_size = float("inf")  # Artificial value for initiating the while-loop
        while num_items < total_size:
            kwargs["params"]["offset"] = num_items
            json = self.request_json(method, path, **kwargs)
            total_size = json.pop("totalSize", None) or json.pop("total", 0)
            key_name, items = json.popitem()
            num_items += len(items)
            all_items.extend(items)

        if len(all_items) != total_size:
            message = f"Expected {total_size} items, but got: {all_items}"
            raise HTTPError(message)

        json = {"totalSize": total_size, key_name: all_items}
        return json

    def get(self, path: str, **kwargs) -> dict[str, Any]:
        """Send an auth'ed GET request and parse the JSON response.

        See ``TowerClient.request`` for argument definitions.

        Returns:
            A dictionary from deserializing the JSON response.
        """
        json = self.request_json("GET", path, **kwargs)
        if "totalSize" in json or "total" in json:
            json = self.request_paged("GET", path, **kwargs)
        return json

    def post(self, path: str, **kwargs) -> dict[str, Any]:
        """Send an auth'ed POST request and parse the JSON response.

        See ``TowerClient.request`` for argument definitions.

        Returns:
            A dictionary from deserializing the JSON response.
        """
        return self.request_json("POST", path, **kwargs)

    def unwrap(self, json: dict[str, Any], key: str) -> Any:
        """Unwrap nested key in JSON response.

        Args:
            json: Raw JSON response.
            key: Top-level key.

        Returns:
            Unnested JSON response.
        """
        if key not in json:
            message = f"Expecting '{key}' key in JSON response ({json})."
            raise HTTPError(message)
        return json[key]

    def get_user_info(self) -> models.User:
        """Describe current user.

        Returns:
            Current user.
        """
        path = "/user-info"
        json = self.get(path)
        unwrapped = self.unwrap(json, "user")
        return models.User.from_json(unwrapped)

    def list_user_workspaces_and_orgs(
        self,
        user_id: int,
    ) -> list[models.Workspace | models.Organization]:
        """List the workspaces and organizations of a given user.

        Returns:
            List of workspaces and organizations.
        """
        path = f"/user/{user_id}/workspaces"
        json = self.get(path)
        items = self.unwrap(json, "orgsAndWorkspaces")
        objects: list[models.Organization | models.Workspace] = list()
        for item in items:
            if item["workspaceId"]:
                workspace = models.Workspace.from_json(item)
                objects.append(workspace)
            else:
                org = models.Organization.from_json(item)
                objects.append(org)
        return objects

    def list_user_workspaces(self) -> list[models.Workspace]:
        """List the workspaces that are available to the current user.

        Returns:
            List of user workspaces.
        """
        user = self.get_user_info()
        items = self.list_user_workspaces_and_orgs(user.id)
        return [item for item in items if isinstance(item, models.Workspace)]

    def generate_params(
        self,
        workspace_id: Optional[int],
        **kwargs,
    ) -> dict[str, Any]:
        """Generate URL query parameters.

        Args:
            workspace_id: Tower workspace ID.
            **kwargs: Additional query parameters that are included
                if they are not set to None.

        Returns:
            URL query parameters based on input.
        """
        params = {}
        if workspace_id:
            params["workspaceId"] = int(workspace_id)
        for name, value in kwargs.items():
            if value is not None:
                params[name] = value
        return params

    def get_compute_env(
        self,
        compute_env_id: str,
        workspace_id: Optional[int] = None,
    ) -> models.ComputeEnv:
        """Retrieve information about a given compute environment.

        Args:
            compute_env_id: Compute environment ID.
            workspace_id: Tower workspace ID.

        Returns:
            Compute environment instance.
        """
        path = f"/compute-envs/{compute_env_id}"
        params = self.generate_params(workspace_id, attributes="labels")
        json = self.get(path, params=params)
        unwrapped = self.unwrap(json, "computeEnv")
        return models.ComputeEnv.from_json(unwrapped)

    def list_compute_envs(
        self,
        workspace_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> list[models.ComputeEnvSummary]:
        """List all compute environments.

        Args:
            workspace_id: Tower workspace ID. Defaults to None.
            status: Compute environment status to filter on.
                Defaults to None.

        Returns:
            List of compute environments.
        """
        path = "/compute-envs"
        params = self.generate_params(workspace_id, status=status)
        json = self.get(path, params=params)
        items = self.unwrap(json, "computeEnvs")
        return [models.ComputeEnvSummary.from_json(item) for item in items]

    def create_label(
        self,
        name: str,
        workspace_id: Optional[int] = None,
    ) -> models.Label:
        """Create a workflow label.

        Args:
            name: Label name.
            workspace_id: Tower workspace ID. Defaults to None.

        Returns:
            Label instance.
        """
        path = "/labels"
        params = self.generate_params(workspace_id)
        payload = {"name": name, "resource": False}
        json = self.post(path, params=params, json=payload)
        return models.Label.from_json(json)

    def list_labels(self, workspace_id: Optional[int] = None) -> list[models.Label]:
        """List all available labels.

        Args:
            workspace_id: Tower workspace ID. Defaults to None.

        Returns:
            List of available labels.
        """
        path = "/labels"
        params = self.generate_params(workspace_id)
        json = self.get(path, params=params)
        items = self.unwrap(json, "labels")
        return [models.Label.from_json(item) for item in items]

    def launch_workflow(
        self,
        launch_info: models.LaunchInfo,
        workspace_id: Optional[int] = None,
    ) -> str:
        """Launch a workflow in the target workspace.

        Args:
            launch_info: Description of which workflow to
                launch and how, including input parameters.
            workspace_id: Tower workspace ID.

        Returns:
            Workflow run ID.
        """
        path = "/workflow/launch"
        params = self.generate_params(workspace_id)
        payload = launch_info.to_json()
        json = self.post(path, params=params, json=payload)
        return self.unwrap(json, "workflowId")

    def get_workflow(
        self,
        workflow_id: str,
        workspace_id: Optional[int] = None,
    ) -> models.Workflow:
        """Get information about a workflow run.

        Attributes:
            workflow_id: The ID number for a workflow run to get
                information about.
            workspace_id: The ID number of the workspace the workflow
                exists within. Defaults to None.

        Returns:
            Workflow instance.
        """
        path = f"/workflow/{workflow_id}"
        params = self.generate_params(workspace_id)
        json = self.get(path=path, params=params)
        unwrapped = self.unwrap(json, "workflow")
        return models.Workflow.from_json(unwrapped)

    def list_workflows(
        self,
        search_filter: Optional[str] = None,
        workspace_id: Optional[int] = None,
    ) -> list[models.Workflow]:
        """List available workflows that match search filter.

        Attributes:
            search_filter: A Nextflow Tower search query, as you would
                compose it in the runs search bar. Defaults to None.
            workspace_id: The ID number of the workspace the workflow
                exists within. Defaults to None.

        Returns:
            List of workflow instances.
        """
        path = "/workflow"
        params = self.generate_params(workspace_id, search=search_filter)
        json = self.get(path=path, params=params)
        items = self.unwrap(json, "workflows")
        return [models.Workflow.from_json(item["workflow"]) for item in items]

    def get_workflow_tasks(
        self,
        workflow_id: str,
        workspace_id: Optional[int] = None,
    ) -> list[models.WorkflowTask]:
        """Retrieve the details of a workflow run's tasks.

        Args:
            workflow_id: The ID number for a workflow run to
            get tasks from.
            workspace_id: The ID number of the workspace the workflow
                exists within. Defaults to None.

        Returns:
            List of WorkflowTask objects.
        """
        path = f"/workflow/{workflow_id}/tasks"
        params = self.generate_params(workspace_id)
        json = self.get(path=path, params=params)
        items = self.unwrap(json, "tasks")
        return [models.WorkflowTask.from_json(item["task"]) for item in items]

    def get_task_logs(
        self, workflow_id: str, task_id: int, workspace_id: Optional[int]
    ) -> str:
        """Retrieve the logs for a given workflow task.

        Args:
            workflow_id: The ID number for a workflow run the
            tasks belongs to.
            task_id: The task_id for the task to get logs from.
            workspace_id: The ID number of the workspace the workflow
                exists within. Defaults to None.

        Returns:
            WorkflowTask Execution logs.
        """
        path = f"/workflow/{workflow_id}/log/{task_id}"
        params = self.generate_params(workspace_id)
        json = self.get(path=path, params=params)
        items = self.unwrap(json, "log")
        log_list = items["entries"]
        return "\n".join(log_list)
