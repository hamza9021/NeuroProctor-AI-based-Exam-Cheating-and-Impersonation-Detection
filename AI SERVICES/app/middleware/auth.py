"""
Request logging middleware.

Logs every HTTP request with its method, path, response status code,
and total processing duration.

This middleware sits at the outermost layer of the request pipeline, so
the duration it measures includes:
  - CORS header processing
  - FastAPI routing
  - Dependency injection (JWT validation, DB lookups)
  - Service / repository execution
  - Response serialisation

Log format:
    INFO | [METHOD] /path → STATUS_CODE (XX.Xms)

This is purely a logging middleware.  JWT authentication is performed
inside the FastAPI dependency layer (app/api/dependencies.py), not here,
so unauthenticated requests are still logged with the correct 401 status.
"""
import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Starlette/FastAPI middleware that emits a structured log line for every
    HTTP request processed by the application.

    Usage (in main.py):
        app.add_middleware(RequestLoggingMiddleware)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Intercept the request, measure duration, and log the result.

        Args:
            request:   The incoming Starlette/FastAPI Request object.
            call_next: The next middleware or route handler in the chain.

        Returns:
            The Response produced by the inner handler.
        """
        start = time.perf_counter()

        # Forward request to the next handler
        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1_000

        # Choose log level based on status code
        if response.status_code >= 500:
            log_fn = logger.error
        elif response.status_code >= 400:
            log_fn = logger.warning
        else:
            log_fn = logger.info

        log_fn(
            "[%s] %s → %d (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
