"""Custom error classes for orca."""


class OrcaError(Exception):
    """Base class for all custom exceptions in orca."""


class ClientRequestError(OrcaError):
    """Client request failed."""


class ConfigError(OrcaError, AttributeError):
    """Missing or invalid configuration attribute(s)."""


class UnexpectedMatchError(OrcaError):
    """A match was found but does not meet expectations."""
