import logging
from dataclasses import field
from typing import ClassVar

from pydantic.dataclasses import dataclass
from synapseclient import Synapse

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

    def monitor_submission_view(self, view_id: str) -> bool:
        """Monitor a submission view for completion.

        Args:
            view_id: The ID of the view to monitor.

        Returns:
            True if there are new "RECEIVED" submissions, False otherwise.
        """
        received_submissions = self.client.tableQuery(
            f"select * from {view_id} where status = 'RECEIVED'"
        )
        recevied_rows = received_submissions.asRowSet()
        return len(recevied_rows["rows"]) > 0
