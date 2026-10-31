from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.errors import BusinessRuleError, ConflictError, DomainError, NotFoundError
from app.routers import employees, review_periods, reviews

STATUS_BY_ERROR = {NotFoundError: 404, ConflictError: 409, BusinessRuleError: 422}


def create_app() -> FastAPI:
    app = FastAPI(
        title="Employee Performance Review API",
        version="1.0.0",
        description="Manager-first performance reviews for every sprint / review period.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    def handle_domain_error(_: Request, exc: DomainError):
        return JSONResponse(status_code=STATUS_BY_ERROR.get(type(exc), 400), content={"detail": str(exc)})

    @app.get("/api/health", tags=["Health"])
    def health():
        return {"status": "ok"}

    for module in (employees, review_periods, reviews):
        app.include_router(module.router, prefix="/api")
    return app


app = create_app()
