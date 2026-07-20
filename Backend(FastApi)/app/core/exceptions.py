"""
Custom exception hierarchy and global FastAPI exception handlers.

Architecture:
  - All domain errors are typed subclasses of AppException.
  - register_exception_handlers() attaches handlers to the FastAPI app.
  - Every handler returns the same JSON error envelope:

        {
            "success": false,
            "message": "Human-readable description",
            "errors": ["Optional list of field-level or detail messages"]
        }

  - This ensures the frontend always receives a predictable error shape,
    regardless of whether the error is a validation failure, auth error,
    or unhandled exception.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# =============================================================================
# Custom exception classes
# =============================================================================

class AppException(Exception):
    """
    Base class for all application-level exceptions.

    Every concrete subclass maps to a specific HTTP status code and is
    caught by the global handler registered in register_exception_handlers().
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: list[str] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.errors: list[str] = errors or []
        super().__init__(message)


class AuthenticationException(AppException):
    """
    401 Unauthorized.

    Raised when:
      - The 'accessToken' cookie is absent.
      - The JWT signature is invalid.
      - The JWT has expired.
      - The JWT payload is missing required fields.
    """

    def __init__(
        self,
        message: str = "Authentication is required to access this resource.",
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, errors)


class AuthorizationException(AppException):
    """
    403 Forbidden.

    Raised when a user is authenticated but their role does not permit
    access to the requested endpoint.
    """

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN, errors)


class NotFoundException(AppException):
    """
    404 Not Found.

    Raised when a requested resource (student, etc.) does not exist
    or has been soft-deleted.
    """

    def __init__(
        self,
        message: str = "The requested resource was not found.",
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND, errors)


class ConflictException(AppException):
    """
    409 Conflict.

    Raised when attempting to create a resource that already exists
    (duplicate registration number, duplicate email, etc.).
    """

    def __init__(
        self,
        message: str = "A resource with the provided details already exists.",
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message, status.HTTP_409_CONFLICT, errors)


class ValidationException(AppException):
    """
    422 Unprocessable Entity (business-level validation).

    Raised for semantic validation errors that pass Pydantic's structural
    checks but fail business rules — e.g. wrong image type, no face detected,
    multiple faces detected, invalid pose name.

    Note: Pydantic structural errors (wrong field type, missing field) are
    caught separately by the RequestValidationError handler below.
    """

    def __init__(
        self,
        message: str = "The request could not be processed due to a validation error.",
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, errors)


class ServiceException(AppException):
    """
    500 Internal Server Error (downstream service failure).

    Raised when Cloudinary, InsightFace, ONNX Runtime, or MongoDB
    encounter an unexpected error that cannot be recovered from.
    """

    def __init__(
        self,
        message: str = "An internal service error occurred. Please try again later.",
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, errors)


# =============================================================================
# Error response builder
# =============================================================================

def _build_error_response(
    message: str,
    errors: list[str],
    status_code: int,
) -> JSONResponse:
    """Construct a standardised JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": errors,
        },
    )


# =============================================================================
# Global exception handler registration
# =============================================================================

def register_exception_handlers(app: FastAPI) -> None:
    """
    Attach all global exception handlers to the FastAPI application.

    Call this in the app factory (main.py) after creating the FastAPI instance
    and before any routers are added.

    Handlers (in precedence order):
      1. AppException        — our custom domain errors
      2. StarletteHTTPException — raised by FastAPI internals (e.g. 404 on
                                  unknown routes, 405 method not allowed)
      3. RequestValidationError — Pydantic field / type validation failures
      4. Exception              — catch-all for truly unexpected errors
    """

    @app.exception_handler(AppException)
    async def handle_app_exception(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(
            "AppException [%d] at %s: %s",
            exc.status_code,
            request.url.path,
            exc.message,
        )
        return _build_error_response(exc.message, exc.errors, exc.status_code)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.warning(
            "HTTPException [%d] at %s: %s",
            exc.status_code,
            request.url.path,
            exc.detail,
        )
        return _build_error_response(
            str(exc.detail), [], exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Format each Pydantic error as "field_path: message"
        errors = [
            "{}: {}".format(
                " → ".join(str(loc) for loc in err["loc"]),
                err["msg"],
            )
            for err in exc.errors()
        ]
        logger.warning(
            "RequestValidationError at %s: %s",
            request.url.path,
            errors,
        )
        return _build_error_response(
            "Request validation failed. Please check the submitted data.",
            errors,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Log the full traceback for debugging
        logger.exception(
            "Unhandled exception at %s: %s", request.url.path, exc
        )
        return _build_error_response(
            "An unexpected internal server error occurred.",
            [],
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
