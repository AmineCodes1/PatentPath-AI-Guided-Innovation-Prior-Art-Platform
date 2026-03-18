"""FastAPI application bootstrap, middleware, and global handlers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import analysis, auth, classifications, health, patents, projects, reports, search
from app.core.config import get_settings
from app.core.database import close_db, init_db
from app.core.exceptions import PatentPathBaseError
from app.core.logging_config import configure_logging
from app.core.redis_client import close_redis, ping_redis

configure_logging()

settings = get_settings()
API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize and teardown shared infrastructure resources."""
    await init_db()
    await ping_redis()
    yield
    await close_redis()
    await close_db()


app = FastAPI(title="PatentPath API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(projects.router, prefix=API_V1_PREFIX)
app.include_router(search.router, prefix=API_V1_PREFIX)
app.include_router(classifications.router, prefix=API_V1_PREFIX)
app.include_router(analysis.router, prefix=API_V1_PREFIX)
app.include_router(patents.router, prefix=API_V1_PREFIX)
app.include_router(reports.router, prefix=API_V1_PREFIX)
app.include_router(health.router, prefix=API_V1_PREFIX)


@app.exception_handler(PatentPathBaseError)
async def patentpath_exception_handler(_: Request, exc: PatentPathBaseError) -> JSONResponse:
    """Return structured domain errors for client-side handling."""
    payload: dict[str, object] = {
        "error_code": exc.error_code,
        "message": exc.message,
    }
    headers: dict[str, str] = {}

    if exc.retry_after_seconds is not None:
        payload["retry_after_seconds"] = exc.retry_after_seconds
        headers["Retry-After"] = str(exc.retry_after_seconds)

    return JSONResponse(status_code=exc.status_code, content=payload, headers=headers or None)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """Handle framework-raised HTTP exceptions with a consistent payload."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Return request validation errors in a stable API format."""
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and avoid leaking internals."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error": str(exc)})
