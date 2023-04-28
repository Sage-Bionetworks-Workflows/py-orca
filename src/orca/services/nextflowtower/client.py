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

    LaunchInfo = models.LaunchInfo

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
        response.raise_for_status()
        return response.json()

    # def request_paged(self, method: str, path: str, **kwargs) -> list[dict[str, Any]]:
    #     """Iterate through pages of results for a given request.

    #     See ``TowerClient.request`` for argument definitions.

    #     Raises:
    #         HTTPError: If the response doesn't match the expectation
    #             for a paged endpoint.

    #     Returns:
    #         The cumulative list of items from all pages.
    #     """
    #     self.update_kwarg(kwargs, "params", "max", 50)
    #     self.update_kwarg(kwargs, "params", "offset", 0)

    #     num_items = 0
    #     total_size = 1  # Artificial value for initiating the while-loop

    #     all_items = list()
    #     while num_items < total_size:
    #         kwargs["params"]["offset"] = num_items
    #         json = self.request_json(method, path, **kwargs)

    #         if "totalSize" not in json:
    #             message = f"'totalSize' not in response JSON ({json}) as expected."
    #             raise HTTPError(message)
    #         total_size = json.pop("totalSize")

    #         if len(json) != 1:
    #             message = f"Expected one other key aside from 'totalSize' ({json})."
    #             raise HTTPError(message)
    #         _, items = json.popitem()

    #         num_items += len(items)
    #         all_items.extend(items)

    #     return all_items

    def get(self, path: str, **kwargs) -> dict[str, Any]:
        """Send an auth'ed GET request and parse the JSON response.

        See ``TowerClient.request`` for argument definitions.

        Returns:
            A dictionary from deserializing the JSON response.
        """
        return self.request_json("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> dict[str, Any]:
        """Send an auth'ed POST request and parse the JSON response.

        See ``TowerClient.request`` for argument definitions.

        Returns:
            A dictionary from deserializing the JSON response.
        """
        return self.request_json("POST", path, **kwargs)

    def unwrap(self, response: dict[str, Any], key: str) -> Any:
        """Unwrap nested key in JSON response.

        Args:
            response: Raw JSON response.
            key: Top-level key.

        Returns:
            Unnested response.
        """
        if key not in response:
            message = f"Expecting '{key}' key in response ({response})."
            raise HTTPError(message)
        return response[key]

    def get_user_info(self) -> dict[str, Any]:
        """Describe current user.

        Returns:
            Current user.
        """
        path = "/user-info"
        response = self.get(path)
        return self.unwrap(response, "user")

    def list_user_workspaces_and_orgs(self, user_id: int) -> list[dict[str, Any]]:
        """List the workspaces and organizations of a given user.

        Returns:
            Workspaces and organizations.
        """
        path = f"/user/{user_id}/workspaces"
        response = self.get(path)
        return self.unwrap(response, "orgsAndWorkspaces")

    def list_user_workspaces(self) -> list[dict[str, Any]]:
        """List the workspaces that are available to the current user.

        Returns:
            List of user workspaces.
        """
        user = self.get_user_info()
        orgs_and_workspaces = self.list_user_workspaces_and_orgs(user["id"])

        workspaces = list()
        for workspace in orgs_and_workspaces:
            # Response includes organizations, which don't have workspace IDs
            if workspace["workspaceId"] is None:
                continue
            workspaces.append(workspace)
        return workspaces

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
    ) -> dict:
        """Retrieve information about a given compute environment.

        Args:
            compute_env_id: Compute environment ID.
            workspace_id: Tower workspace ID.

        Returns:
            Information about the compute environment.
        """
        path = f"/compute-envs/{compute_env_id}"
        params = self.generate_params(workspace_id)
        response = self.get(path, params=params)
        return self.unwrap(response, "computeEnv")

    def list_compute_envs(
        self,
        workspace_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> dict:
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
        response = self.get(path, params=params)
        return self.unwrap(response, "computeEnvs")

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
            Workflow ID.
        """
        path = "/workflow/launch"
        params = self.generate_params(workspace_id)
        payload = launch_info.to_dict()
        response = self.post(path, params=params, json=payload)
        return self.unwrap(response, "workflowId")
