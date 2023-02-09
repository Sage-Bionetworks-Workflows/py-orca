"""Custom error classes for orca."""


class OrcaError(Exception):
    """Base class for all custom exceptions in orca."""


class ClientRequestError(OrcaError):
    """Client request failed."""


class ClientArgsError(OrcaError):
    """Client arguments are missing or invalid."""


class OptionalAttrRequiredError(OrcaError):
    """Optional attribute is required in this context."""


class UnexpectedMatchError(OrcaError):
    """A match was found but does not meet expectations."""
