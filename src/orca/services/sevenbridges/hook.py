from orca.services.base.hook import BaseOrcaHook
from orca.services.sevenbridges.config import SevenBridgesConfig
from orca.services.sevenbridges.ops import SevenBridgesOps


class SevenBridgesHook(BaseOrcaHook):
    """Wrapper around SevenBridges client and ops classes.

    Class Variables:
        conn_name_attr: Inherited Airflow attribute (e.g., "sbg_conn_id").
        default_conn_name: Inherited Airflow attribute (e.g., "sbg_default").
        conn_type: Inherited Airflow attribute (e.g., "sbg").
        hook_name: Inherited Airflow attribute (e.g., "SevenBridges").
        ops_class: The Ops class for this service.
        config_class: The configuration class for this service.
    """

    conn_name_attr = "sbg_conn_id"
    default_conn_name = "sbg_default"
    conn_type = "sbg"
    hook_name = "SevenBridges"

    ops_class = SevenBridgesOps
    config_class = SevenBridgesConfig
