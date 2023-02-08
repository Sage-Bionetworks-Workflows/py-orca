class OrcaError(Exception):
    """Base class for all custom exceptions in orca."""


class ClientRequestError(OrcaError):
    """Client request failed."""


class ClientArgsError(OrcaError):
    """Client arguments are missing or invalid."""
