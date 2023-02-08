"""Module for interacting with third-party services.

Each service has its own module with one or more submodules:

client.py (optional):
    This submodule defines a client class that interacts with the
    service/API. Services with an existing third-party Python client
    do not need this submodule.
client_factory.py:
    This submodule defines a convenience factory class that features
    methods related to client construction, such as argument "sourcing"
    (e.g., from environment variables) and validation. Eventually, these
    classes might also pull information from a configuration file.
tasks.py:
    This submodule defines a tasks class that performs common operations
    using a third-party client or the one defined in `client.py`. These
    classes might feature low-level methods depending on the client's
    functionality. That said, their aim is to offer high-level methods
    that can be used for building data pipelines. That said, a important
    feature of operations available in this submodule is that they
    strive to be idempotent. In other words, they take additional steps
    to return the same output given the same input. For example, an
    operation that launches a workflow should make sure that one wasn't
    already launched previously; if so, return that workflows ID rather
    than launching a new workflow. Idempotency might not always be
    possible due to limitations with the service. For instance, the
    service might not offer querying functionality to retrieve a
    previously created artifact (e.g., workflow run). These cases
    should be handled with care (and we might eventually implement
    helper functions/decorators to overcome this limitation).
    Eventually, these classes might also pull information from a
    configuration file.
hook.py
    This submodule defines an Airflow hook that initializes the tasks
    class from `tasks.py` using the credentials defined by an Airflow
    connection. These hook classes are deliberately thin wrappers around
    the tasks classes. The aim here is to minimize Airflow-specific
    code, which is harder to test. This hook also takes advantage of
    extra field associated with connection objects to configure the
    underlying client and/or tasks objects. Whether to include a value
    as the extra connection field probably depends on whether that
    value is useful to change the overall state of the underlying
    client and/or tasks objects (e.g., `project` for SevenBridgesTasks)
    and whether the value is invariable for a given DAG. Eventually,
    these classes might also pull information from a configuration file.
"""
