"""
NeuroProctor FastAPI AI Backend — Application Entry Point.

This module is responsible for:
  1. Creating the FastAPI application instance (create_app factory).
  2. Registering all middleware (CORS, request logging).
  3. Attaching global exception handlers.
  4. Including API routers.
  5. Managing the application lifespan (startup + shutdown events).

Startup sequence (order matters):
  a. MongoDB — must be up before any request is served.
  b. Cloudinary — stateless SDK config, very fast.
  c. InsightFace model — slowest step (~3–10s on first cold start).
     Runs inside a thread-pool so the event loop stays non-blocking.

Shutdown sequence:
  a. MongoDB connection pool — gracefully drained and closed.

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Or via the __main__ guard:
    python main.py
"""
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.cloudinary_config import init_cloudinary
from app.config.database import close_mongo_connection, connect_to_mongo
from app.config.settings import settings
from app.core.exceptions import register_exception_handlers
from app.middleware.auth import RequestLoggingMiddleware
from app.services.embedding_service import embedding_service

# =============================================================================
# Logging configuration
# =============================================================================
# Configure root logger once here.  All module-level loggers (via
# logging.getLogger(__name__)) will inherit this configuration.
logging.basicConfig(
    level=logging.DEBUG if settings.APP_DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Silence overly verbose third-party loggers in production
if not settings.APP_DEBUG:
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("cloudinary").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# =============================================================================
# Lifespan context manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage the application startup and shutdown lifecycle.

    Everything before `yield` runs on startup.
    Everything after `yield` runs on shutdown.

    Resources initialised here are available to all request handlers
    through the module-level singletons defined in each service module.
    This ensures:
      - No per-request model loading.
      - No per-request DB reconnections.
      - Clean resource release on shutdown.
    """
    # ── STARTUP ──────────────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("  NeuroProctor AI Backend — Starting up")
    logger.info("  Environment : %s", settings.APP_ENV)
    logger.info("  Version     : %s", settings.APP_VERSION)
    logger.info("  Host:Port   : %s:%d", settings.APP_HOST, settings.APP_PORT)
    logger.info("  Debug Mode  : %s", settings.APP_DEBUG)
    logger.info("═" * 60)

    # a. Connect to MongoDB and create indexes
    await connect_to_mongo()

    # b. Configure Cloudinary SDK (synchronous, fast)
    init_cloudinary()

    # c. Load InsightFace buffalo_l model (slow — runs in thread-pool)
    #    This is the most expensive startup step.  On first run, InsightFace
    #    downloads the model weights (~300 MB).  Subsequent startups are fast.
    await embedding_service.initialize()

    logger.info("=" * 60)
    logger.info("  All services initialised. Ready to accept requests.")
    logger.info("  API Docs : http://%s:%d/api/docs", settings.APP_HOST, settings.APP_PORT)
    logger.info("=" * 60)

    yield  # ──────────────── Application is running ────────────────

    # ── SHUTDOWN ─────────────────────────────────────────────────────────────
    logger.info("Shutting down NeuroProctor AI Backend …")
    await close_mongo_connection()
    logger.info("Shutdown complete. Goodbye.")


# =============================================================================
# Application factory
# =============================================================================

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Returns a fully configured FastAPI app ready to be served by Uvicorn.
    This factory pattern makes the app testable (instantiate a fresh app
    in tests without running the lifespan).

    Returns:
        FastAPI — the configured application instance.
    """
    application = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        # API documentation endpoints
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        # Contact metadata for OpenAPI spec
        contact={
            "name": "NeuroProctor Team",
            "url": "https://github.com/hamza9021/NeuroProctor",
        },
        license_info={
            "name": "MIT",
        },
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    # allow_credentials=True is REQUIRED for HttpOnly cookie forwarding.
    # The browser will not send cookies unless this is set AND the request
    # origin matches allow_origins exactly.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.CORS_ORIGIN],
        allow_credentials=True,  # ← Critical: enables HttpOnly cookie forwarding
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
        ],
    )

    # ── Request logging middleware ─────────────────────────────────────────────
    # Added AFTER CORSMiddleware so CORS errors are also logged.
    application.add_middleware(RequestLoggingMiddleware)

    # ── Global exception handlers ─────────────────────────────────────────────
    # Must be registered before routers so handlers are in place for all routes.
    register_exception_handlers(application)

    # ── API routers ───────────────────────────────────────────────────────────
    # Import here (inside factory) to avoid circular import issues at module load.
    from app.api.routes import health, student

    application.include_router(health.router, prefix="/api/v1")
    application.include_router(student.router, prefix="/api/v1")

    logger.debug(
        "Registered routes: %s",
        [getattr(route, "path", str(route)) for route in application.routes],
    )

    return application


# =============================================================================
# Application instance
# =============================================================================
# This module-level `app` is what Uvicorn imports:
#   uvicorn main:app --reload
app: FastAPI = create_app()


# =============================================================================
# Entry point (for direct execution: python main.py)
# =============================================================================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level="debug" if settings.APP_DEBUG else "info",
        # Proxy headers for deployment behind nginx / load balancers
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
