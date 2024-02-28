"""
Handles Synapse operations for py-orca services.
"""
import logging
from dataclasses import field
from functools import cached_property
from typing import ClassVar, List, Union

from challengeutils import utils
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

        Arguments:
            evaluation_id: The Synapse ID of the queue to monitor.

        Returns:
            True if there are "RECEIVED" submissions, False otherwise.
        """
        received_submissions = self.client.getSubmissionBundles(
            evaluation_id, status="RECEIVED"
        )
        submissions_num = sum(1 for submission in received_submissions)
        return submissions_num > 0

    def trigger_indexing(self, synapse_view: str) -> None:
        """
        Trigger indexing in Synapse.

        Arguments:
            syn: A Synapse object.
            synapse_view: The Synapse ID of the view.
        """
        self.client.tableQuery(f"select * from {synapse_view} limit 1")

    def get_submissions_with_status(
        self, submission_view: str, submission_status: str = "RECEIVED"
    ) -> List[str]:
        """
        Get all submissions with desired submission status in a Synapse
        submission view.

        Arguments:
            submission_view: The Synapse ID of the table view to get submissions from.
            submission_status: The submission status to filter for.
                               Defaults to "RECEIVED".

        Returns:
            A list of submission IDs.

        """
        # Trigger indexing
        self.trigger_indexing(submission_view)

        # Get all submissions for the given ``submission_view``
        query_results = self.client.tableQuery(
            f"select * from {submission_view} where status = '{submission_status}'"
        )

        submission_ids = query_results.asDataFrame()["id"].tolist()

        return submission_ids

    def update_submissions_status(
        self,
        submission_ids: Union[int, str, List[Union[int, str]]],
        submission_status: str,
    ) -> None:
        """
        Update the status of one or more submissions in Synapse.

        Arguments:
            submission_ids: The Synapse ID of the submission(s).
            submission_status: The new status of the submission(s).

        """

        # Prepare a single submission_id for the for-loop
        if type(submission_ids) in [str, int]:
            submission_ids = [submission_ids]

        # Let's catch for anything that was fed that is NOT a str, int, or list
        if not isinstance(submission_ids, list):
            raise TypeError(
                "``submission_ids`` must be a string, int, or list of either/both."
            )
        if not all(type(id) in [str, int] for id in submission_ids):
            raise TypeError(
                "``submission_ids`` must be a string, int, or list of either/both."
            )

        # Update submission status(es)
        for id in submission_ids:
            utils.change_submission_status(
                self.client, submissionid=id, status=submission_status
            )
