from orca.services.base.hook import BaseOrcaHook
from orca.services.nextflowtower.config import NextflowTowerConfig
from orca.services.nextflowtower.ops import NextflowTowerOps


class NextflowTowerHook(BaseOrcaHook):
    """Wrapper around Nextflow Tower client and ops classes.

    Class Variables:
        conn_name_attr: Inherited Airflow attribute (e.g., "sbg_conn_id").
        default_conn_name: Inherited Airflow attribute (e.g., "sbg_default").
        conn_type: Inherited Airflow attribute (e.g., "sbg").
        hook_name: Inherited Airflow attribute (e.g., "SevenBridges").
        ops_class: The Ops class for this service.
        config_class: The configuration class for this service.
    """

    conn_name_attr = "tower_conn_id"
    default_conn_name = "tower_default"
    conn_type = "tower"
    hook_name = "NextflowTower"

    ops_class = NextflowTowerOps
    config_class = NextflowTowerConfig
