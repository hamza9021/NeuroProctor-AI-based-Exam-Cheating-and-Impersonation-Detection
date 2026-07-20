"""
JWT verification module.

Decodes and validates the JSON Web Token issued by the Express backend.

Express token signing (from user.models.js):
    jwt.sign(
        { _id: this._id, email: this.email, fullName: this.fullName, role: this.role },
        process.env.ACCESS_TOKEN_SECRET,
        { expiresIn: process.env.ACCESS_TOKEN_EXPIRY }
    )

Key observations:
  - Algorithm  : HS256 (jsonwebtoken default)
  - Payload    : _id (not id), email, fullName, role
  - No 'aud'   : Express does not set audience, so we skip aud verification
  - Secret     : Shared via ACCESS_TOKEN_SECRET environment variable

This module performs only token verification and payload extraction.
It does NOT touch the database — that responsibility belongs to the
dependency layer (app/api/dependencies.py).
"""
import logging

from jose import ExpiredSignatureError, JWTError, jwt

from app.config.settings import settings
from app.core.exceptions import AuthenticationException

logger = logging.getLogger(__name__)

# Fields that must be present in the JWT payload for the token to be considered valid.
_REQUIRED_PAYLOAD_FIELDS: tuple[str, ...] = ("_id", "email", "role")


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token signed by the Express backend.

    Performs:
      1. Signature verification using ACCESS_TOKEN_SECRET (HMAC-SHA256).
      2. Expiry check (raises AuthenticationException if expired).
      3. Required field presence check.
      4. Payload field remapping (_id → user_id, fullName → full_name).

    Args:
        token: Raw JWT string extracted from the 'accessToken' HttpOnly cookie.

    Returns:
        A plain dict with keys: user_id, email, full_name, role.

    Raises:
        AuthenticationException (401):
            - Token has expired.
            - Signature is invalid / token is malformed.
            - Required payload fields are missing.
    """
    try:
        payload: dict = jwt.decode(
            token,
            settings.ACCESS_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            # Express does not set 'aud', so skip audience verification.
            options={"verify_aud": False},
        )
    except ExpiredSignatureError:
        logger.warning("JWT token rejected — token has expired.")
        raise AuthenticationException(
            "Your session has expired. Please log in again through the main application."
        )
    except JWTError as exc:
        logger.warning("JWT decode error: %s", exc)
        raise AuthenticationException(
            "The provided token is invalid or has been tampered with."
        )

    # Verify all required fields are present in the decoded payload
    missing_fields = [
        field for field in _REQUIRED_PAYLOAD_FIELDS if field not in payload
    ]
    if missing_fields:
        logger.warning(
            "JWT payload is missing required fields: %s", missing_fields
        )
        raise AuthenticationException(
            f"Token payload is malformed — missing fields: {missing_fields}"
        )

    # Remap Express field names to Python-idiomatic names:
    #   _id      → user_id   (MongoDB ObjectId string)
    #   fullName → full_name (snake_case)
    return {
        "user_id": str(payload["_id"]),
        "email": payload["email"],
        "full_name": payload.get("fullName", ""),
        "role": payload["role"],
    }
