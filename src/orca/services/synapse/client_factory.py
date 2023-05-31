from pydantic.dataclasses import dataclass
from synapseclient import Synapse
from synapseclient.core.exceptions import SynapseAuthenticationError

from orca.errors import ConfigError
from orca.services.base.client_factory import BaseClientFactory
from orca.services.synapse.config import SynapseConfig


@dataclass(kw_only=False)
class SynapseClientFactory(BaseClientFactory):
    """Factory for constructing Synapse clients.

    Attributes:
        config: Configuration object for this service.

    Class Variables:
        client_class: The client class for this service.
    """

    config: SynapseConfig

    client_class = Synapse

    def create_client(self) -> Synapse:
        """Create an authenticated client.

        Typically, this involves pulling values from the configuration,
        ensuring that non-optional arguments are not set to None, and
        using them to instantiate a client class.

        Raises:
            ConfigError: If the configuration is invalid.

        Returns:
            An authenticated client object.
        """
        client = Synapse(silent=True)
        auth_token = self.config.auth_token

        if auth_token is None:
            message = f"Config ({self.config}) is missing auth_token."
            raise ConfigError(message)

        # Ignore authentication error (leave that to `test_client_request`)
        try:
            client.login(authToken=auth_token)
        except SynapseAuthenticationError:
            pass

        return client

    @classmethod
    def test_client_request(cls, client: Synapse) -> None:
        """Make a test request with an authenticated request.

        This method does not need to perform any error handling.
        That is taken care of by the ``test_client()`` method.
        That said, this method can raise an error if a response
        is made but indicates a problem.

        Args:
            client: An authenticated client for this service.
        """
        profile = client.getUserProfile()
        if profile.get("userName") == "anonymous":
            message = "Client is accessing Synapse anonymously."
            raise SynapseAuthenticationError(message)
        else:  # pragma: no cover
            pass  # To ignore lack of test coverage for happy path
