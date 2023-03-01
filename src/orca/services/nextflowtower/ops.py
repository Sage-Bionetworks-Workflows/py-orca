from functools import cached_property

from pydantic.dataclasses import dataclass

from orca.errors import ConfigError
from orca.services.base.ops import BaseOps
from orca.services.nextflowtower.client_factory import NextflowTowerClientFactory
from orca.services.nextflowtower.config import NextflowTowerConfig


@dataclass(kw_only=False)
class NextflowTowerOps(BaseOps):
    """Collection of operations for Nextflow Tower.

    Attributes:
        config: A configuration object for this service.

    Class Variables:
        client_factory_class: The class for constructing clients.
    """

    config: NextflowTowerConfig

    client_factory_class = NextflowTowerClientFactory

    @cached_property
    def workspace(self) -> int:
        """The currently active Nextflow Tower workspace."""
        if self.config.workspace is None:
            message = f"Config ({self.config}) does not specify a workspace."
            raise ConfigError(message)
        return self.config.workspace
