class DomainError(Exception):
    """Base for errors raised by the service layer."""


class NotFoundError(DomainError):
    """A requested record does not exist (HTTP 404)."""


class ConflictError(DomainError):
    """The request clashes with existing data (HTTP 409)."""


class BusinessRuleError(DomainError):
    """The request breaks a business rule (HTTP 422)."""
