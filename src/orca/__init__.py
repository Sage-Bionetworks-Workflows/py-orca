"""Top-level module for orca."""

# isort: skip_file

from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

import logging

# Capture warnings made with the warnings standard module
logging.captureWarnings(True)

# Configure a stream handler
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Configure a module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(handler)

# Silence Airflow logging
logging.getLogger("airflow").setLevel(logging.ERROR)
