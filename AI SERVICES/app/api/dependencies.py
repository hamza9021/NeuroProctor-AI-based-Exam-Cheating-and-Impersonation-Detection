"""
FastAPI dependency functions for JWT authentication and role authorisation.

These dependencies form the security gate for every protected endpoint.

Dependency chain:
    HTTP Request
        │
        ▼
    get_current_user(request)
        │  reads 'accessToken' cookie
        │  calls decode_access_token() → validates JWT, remaps payload fields
        │  returns TokenPayload
        ▼
    require_roles(["admin", "invigilator"])
        │  factory function returns _role_checker dependency
        │  _role_checker checks TokenPayload.role ∈ allowed_roles
        │  returns TokenPayload (or raises 403)

Usage in route handlers:
    from app.api.dependencies import require_roles
    from app.schemas.student import TokenPayload
    from fastapi import Depends

    _protected = require_roles(["admin", "invigilator"])

    @router.post("/students")
    async def create_student(
        ...,
        current_user: TokenPayload = Depends(_protected),
    ):
        ...  # current_user.user_id, .email, .role are available here

Error responses:
    401 Unauthorized — cookie missing / token expired / token invalid
    403 Forbidden    — role not in allowed_roles
"""
import logging
from typing import Callable

from fastapi import Depends, Request

from app.config.security import JWT_COOKIE_NAME
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.jwt import decode_access_token
from app.schemas.student import TokenPayload

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> TokenPayload:
    """
    FastAPI dependency that extracts and validates the JWT from the request cookie.

    The Express backend stores the access token as an HttpOnly cookie named
    'accessToken' on the response after login.  This dependency reads that
    cookie from every incoming request and validates the JWT signature using
    the shared ACCESS_TOKEN_SECRET.

    Args:
        request: The incoming FastAPI request object (injected by FastAPI).

    Returns:
        TokenPayload — structured payload with user_id, email, full_name, role.

    Raises:
        AuthenticationException (401):
            - Cookie 'accessToken' is not present in the request.
            - JWT has expired.
            - JWT signature is invalid or token is malformed.
            - JWT payload is missing required fields (_id, email, role).
    """
    token: str | None = request.cookies.get(JWT_COOKIE_NAME)

    if not token:
        raise AuthenticationException(
            f"Authentication cookie '{JWT_COOKIE_NAME}' is missing. "
            "Please log in through the main NeuroProctor application."
        )

    # decode_access_token handles all JWT-level errors and raises
    # AuthenticationException with descriptive messages.
    payload_dict: dict = decode_access_token(token)

    user = TokenPayload(**payload_dict)
    logger.debug(
        "Authenticated — user_id: %s | role: %s | email: %s",
        user.user_id,
        user.role,
        user.email,
    )
    return user


def require_roles(allowed_roles: list[str]) -> Callable:
    """
    Dependency factory for role-based access control (RBAC).

    Returns a FastAPI dependency function that:
      1. Calls get_current_user() to authenticate the request.
      2. Verifies the authenticated user's role is in *allowed_roles*.
      3. Returns the TokenPayload if authorised.
      4. Raises AuthorizationException (403) if the role is not permitted.

    The factory pattern means the dependency is created once per router
    definition (not per request), making it very lightweight at request time.

    Args:
        allowed_roles: List of role strings permitted to access the endpoint.
                       Example: ["admin", "invigilator"]

    Returns:
        An async dependency callable that resolves to TokenPayload.

    Example:
        _protected = require_roles(["admin", "invigilator"])

        @router.delete("/{id}")
        async def delete_student(
            id: str,
            current_user: TokenPayload = Depends(_protected),
        ):
            ...
    """

    async def _role_checker(
        user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        """
        Inner dependency: checks that the authenticated user has a permitted role.

        Raises:
            AuthorizationException (403): User role is not in allowed_roles.
        """
        if user.role not in allowed_roles:
            logger.warning(
                "Authorisation denied — user_id: %s | role: '%s' | "
                "required roles: %s | endpoint access refused.",
                user.user_id,
                user.role,
                allowed_roles,
            )
            raise AuthorizationException(
                f"Access denied. Your role ('{user.role}') is not authorised "
                f"to perform this action. Required roles: {allowed_roles}."
            )

        return user

    return _role_checker
