from typing import Any

import requests
from pydantic.dataclasses import dataclass
from requests.exceptions import HTTPError


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

    def update_kwarg(
        self, kwargs: dict[str, Any], key1: str, key2: str, default: Any
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
        valid_methods = {"GET", "PUT", "POST", "DELETE"}
        if method not in valid_methods:
            message = f"Method ({method}) not among valid options ({valid_methods})."
            raise ValueError(message)

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

    def request_paged(self, method: str, path: str, **kwargs) -> list[dict[str, Any]]:
        """Iterate through pages of results for a given request.

        See ``TowerClient.request`` for argument definitions.

        Raises:
            HTTPError: If the response doesn't match the expectation
                for a paged endpoint.

        Returns:
            The cumulative list of items from all pages.
        """
        self.update_kwarg(kwargs, "params", "max", 50)
        self.update_kwarg(kwargs, "params", "offset", 0)

        num_items = 0
        total_size = 1  # Artificial value for initiating the while-loop

        all_items = list()
        while num_items < total_size:
            kwargs["params"]["offset"] = num_items
            json = self.request_json(method, path, **kwargs)

            if "totalSize" not in json:
                message = f"'totalSize' not in response JSON ({json}) as expected."
                raise HTTPError(message)
            total_size = json.pop("totalSize")

            if len(json) != 1:
                message = f"Expected one other key aside from 'totalSize' ({json})."
                raise HTTPError(message)
            _, items = json.popitem()

            num_items += len(items)
            all_items.extend(items)

        return all_items

    def get(self, path: str, **kwargs) -> dict[str, Any]:
        """Send an auth'ed GET request and parse the JSON response.

        See ``TowerClient.request`` for argument definitions.

        Returns:
            A dictionary from deserializing the JSON response.
        """
        return self.request_json("GET", path, **kwargs)

    # TODO: Consider creating a `client` submodule folder to organize methods
    def get_user_info(self) -> dict[str, Any]:
        """Describe current user.

        Returns:
            Current user
        """
        path = "/user-info"
        return self.get(path)
