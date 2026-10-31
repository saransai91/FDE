"""Maps domain errors to HTTP responses in the standard {"detail": ...} format."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import BusinessRuleError, ConflictError, DomainError, NotFoundError

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: 404,
    ConflictError: 409,
    BusinessRuleError: 422,
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=STATUS_BY_ERROR.get(type(exc), 400), content={"detail": exc.message})
