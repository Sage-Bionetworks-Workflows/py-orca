import logging
from dataclasses import field
from functools import cached_property
from typing import ClassVar

from pydantic.dataclasses import dataclass
from synapseclient import Synapse
from synapsefs import SynapseFS

from orca.errors import ConfigError
from orca.services.base.ops import BaseOps
from orca.services.synapse.client_factory import SynapseClientFactory
from orca.services.synapse.config import SynapseConfig

logger = logging.getLogger(__name__)


@dataclass(kw_only=False)
class SynapseOps(BaseOps):
    """Collection of operations for Synapse.

    Attributes:
        config: A configuration object for this service.

    Class Variables:
        client_factory_class: The class for constructing clients.
    """

    config: SynapseConfig = field(default_factory=SynapseConfig)

    client_factory_class = SynapseClientFactory

    client: ClassVar[Synapse]

    @cached_property
    def fs(self) -> SynapseFS:
        """Synapse file system."""
        auth_token = self.config.auth_token

        if auth_token is None:
            message = f"Config ({self.config}) is missing auth_token."
            raise ConfigError(message)

        return SynapseFS(auth_token=auth_token)

    def monitor_evaluation_queue(self, evaluation_id: str) -> bool:
        """Monitor an evaluation queue in Synapse.

        Args:
            evaluation_id: The Synapse ID of the queue to monitor.

        Returns:
            True if there are "RECEIVED" submissions, False otherwise.
        """
        received_submissions = self.client.getSubmissionBundles(
            evaluation_id, status="RECEIVED"
        )
        submissions_num = sum(1 for submission in received_submissions)
        return submissions_num > 0
