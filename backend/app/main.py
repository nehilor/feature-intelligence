import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.feature_analysis import router as feature_analysis_router
from app.api.feature_decision import router as feature_decision_router
from app.api.feature_decision_brief import router as feature_decision_brief_router
from app.api.feature_priority import router as feature_priority_router
from app.api.feature_relationships import router as feature_relationships_router
from app.api.feature_requests import router as feature_requests_router
from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.persistence.database import init_database

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    init_database(settings.database_url)
    logger.info("Application startup complete (app_env=%s)", settings.app_env)
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Feature Intelligence API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(feature_requests_router, prefix="/api")
    app.include_router(feature_analysis_router, prefix="/api")
    app.include_router(feature_relationships_router, prefix="/api")
    app.include_router(feature_priority_router, prefix="/api")
    app.include_router(feature_decision_brief_router, prefix="/api")
    app.include_router(feature_decision_router, prefix="/api")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()
