import pytest

from orca.errors import ConfigError
from orca.services.synapse import SynapseOps


def test_for_an_error_when_accessing_fs_without_credentials(
    patch_os_environ, syn_project_id
):
    ops = SynapseOps()
    with pytest.raises(ConfigError):
        ops.fs.listdir(syn_project_id)
