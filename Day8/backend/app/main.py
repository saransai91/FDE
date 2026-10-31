"""FastAPI app (BFF). Run from Day8/backend:  uvicorn app.main:app --reload"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import employees, review_periods, reviews
from app.api.errors import register_error_handlers
from app.config import settings

API_PREFIX = "/api"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Employee Performance Review API",
        version="1.0.0",
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"],  # the React list reads the total from this header
    )
    register_error_handlers(app)
    for module in (employees, review_periods, reviews):
        app.include_router(module.router, prefix=API_PREFIX)

    @app.get("/", include_in_schema=False)
    def root():
        return {"message": "Performance Review API is running", "docs": f"{API_PREFIX}/docs"}

    return app


app = create_app()
