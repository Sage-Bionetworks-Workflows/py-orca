from orca.services.base.hook import BaseOrcaHook
from orca.services.synapse.config import SynapseConfig
from orca.services.synapse.ops import SynapseOps


class SynapseHook(BaseOrcaHook):
    """Wrapper around Synapse client and ops classes.

    Class Variables:
        conn_name_attr: Inherited Airflow attribute (e.g., "sbg_conn_id").
        default_conn_name: Inherited Airflow attribute (e.g., "sbg_default").
        conn_type: Inherited Airflow attribute (e.g., "sbg").
        hook_name: Inherited Airflow attribute (e.g., "SevenBridges").
        ops_class: The Ops class for this service.
        config_class: The configuration class for this service.
    """

    conn_name_attr = "synapse_conn_id"
    default_conn_name = "synapse_default"
    conn_type = "syn"
    hook_name = "Synapse"

    ops_class = SynapseOps
    config_class = SynapseConfig
