from typing import Any

from orca import __version__
from orca.services.sevenbridges.hook import SevenBridgesHook


def generate_connection_type(hook) -> dict[str, str]:
    """Generate an Airflow-compatible connection type.

    Args:
        hook: An Airflow hook.

    Returns:
        An Airflow-compatible connection type.
    """
    return {
        "connection-type": hook.conn_type,
        "hook-class-name": f"{hook.__module__}.{hook.__name__}",
    }


def get_provider_info() -> dict[str, Any]:
    """Generate provider info to register as an Airflow provider.

    Adapted from this Astronomer repository (commit SHA: 212e14ed):
    https://github.com/astronomer/airflow-provider-sample

    Returns:
        Provider information for Airflow according to this schema:
        https://github.com/apache/airflow/blob/main/airflow/provider_info.schema.json
    """
    return {
        "package-name": "py-orca",
        "versions": [__version__],
        "name": "ORCA Airflow Provider (Sage Bionetworks)",
        "description": "Package for connecting services and building data pipelines.",
        "connection-types": [
            generate_connection_type(SevenBridgesHook),
        ],
        # TODO: Add links to uploaded files (e.g., on Synapse) for Synapse operators
        # "extra-links": ["sample_provider.operators.sample.SampleOperatorExtraLink"],
    }
