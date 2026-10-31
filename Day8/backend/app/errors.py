"""Domain errors raised by services/repositories. The API layer maps them to HTTP codes."""


class DomainError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """-> 404"""


class ConflictError(DomainError):
    """-> 409 (e.g. duplicate review for employee + period, BR-3)"""


class BusinessRuleError(DomainError):
    """-> 422 (closed period, inactive employee, unknown ids)"""
