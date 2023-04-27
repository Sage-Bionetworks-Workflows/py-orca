from pydantic.dataclasses import dataclass

from orca.errors import ConfigError
from orca.services.base.client_factory import BaseClientFactory
from orca.services.nextflowtower.client import NextflowTowerClient
from orca.services.nextflowtower.config import NextflowTowerConfig


@dataclass(kw_only=False)
class NextflowTowerClientFactory(BaseClientFactory):
    """Factory for constructing Nextflow Tower clients.

    Attributes:
        config: Configuration object for this service.

    Class Variables:
        client_class: The client class for this service.
    """

    config: NextflowTowerConfig

    client_class = NextflowTowerClient

    def create_client(self) -> NextflowTowerClient:
        """Create an authenticated client.

        Typically, this involves pulling values from the configuration,
        ensuring that non-optional arguments are not set to None, and
        using them to instantiate a client class.

        Raises:
            ConfigError: If the configuration is invalid.

        Returns:
            An authenticated client object.
        """
        kwargs = dict()
        api_endpoint = self.config.api_endpoint
        auth_token = self.config.auth_token

        if api_endpoint is None or auth_token is None:
            message = f"Config ({self.config}) is missing api_endpoint or auth_token."
            raise ConfigError(message)

        kwargs["api_endpoint"] = api_endpoint.rstrip("/")
        kwargs["auth_token"] = auth_token

        return NextflowTowerClient(**kwargs)

    @classmethod
    def test_client_request(cls, client: NextflowTowerClient) -> None:
        """Make a test request with an authenticated request.

        This method does not need to perform any error handling.
        That is taken care of by the ``test_client()`` method.
        That said, this method can raise an error if a response
        is made but indicates a problem.

        Args:
            client: An authenticated client for this service.
        """
        client.get_user_info()
