"""Module for interacting with third-party services.

Each service has its own module with one or more submodules:

client.py (optional):
    This submodule defines a client class that interacts with the
    service/API. Services with an existing third-party Python client
    do not need this submodule.
client_factory.py:
    This submodule defines a convenience factory class that features
    methods related to client construction, such as argument "sourcing"
    (e.g., from environment variables) and validation.
tasks.py:
    This submodule defines a tasks class that performs common operations
    using a third-party client or the one defined in `client.py`. These
    classes might feature low-level methods depending on the client's
    functionality. That said, their aim is to offer high-level methods
    that can be used for building data pipelines.
hook.py
    This submodule defines an Airflow hook that initializes the tasks
    class from `tasks.py` using the credentials defined by an Airflow
    connection. These hook classes are deliberately thin wrappers around
    the tasks classes. The aim here is to minimize Airflow-specific
    code, which is harder to test.
"""
