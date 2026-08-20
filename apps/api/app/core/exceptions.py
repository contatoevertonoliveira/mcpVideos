"""Base error hierarchy (Documento 02, secao 50).

Subclasses especificas (WorkflowError, ProviderError, BudgetExceededError,
etc.) chegam junto com os modulos que as originam, a partir da Fase 02 em
diante. Nao expor stack traces ao usuario final.
"""

from __future__ import annotations


class ApplicationError(Exception):
    """Base for every error the application raises intentionally.

    ``http_status`` is fixed per exception class (it describes the kind of
    failure). ``code`` is the specific, business-readable error code and may
    be overridden per instance (e.g. "PROJECT_NOT_FOUND" for a NotFoundError).
    """

    http_status: int = 400
    code: str = "APPLICATION_ERROR"
    message: str = "Something went wrong."

    def __init__(self, message: str | None = None, code: str | None = None) -> None:
        self.message = message or self.message
        self.code = code or self.code
        super().__init__(self.message)


class DomainError(ApplicationError):
    http_status = 400
    code = "DOMAIN_ERROR"


class AuthenticationError(ApplicationError):
    http_status = 401
    code = "AUTHENTICATION_ERROR"


class AuthorizationError(ApplicationError):
    http_status = 403
    code = "AUTHORIZATION_ERROR"


class NotFoundError(ApplicationError):
    http_status = 404
    code = "NOT_FOUND"
