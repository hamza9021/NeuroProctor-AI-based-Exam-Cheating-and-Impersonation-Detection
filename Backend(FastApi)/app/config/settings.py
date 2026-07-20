"""
Application-wide settings loaded from environment variables.

Uses Pydantic BaseSettings so that:
  1. Every variable is declared with a Python type (type-safety at startup).
  2. Values are read from the .env file automatically.
  3. Missing required variables raise a clear ValidationError on startup
     (fail-fast rather than failing at first use).

Access settings anywhere via the module-level singleton:
    from app.config.settings import settings
"""
from functools import lru_cache
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All environment-configurable application settings."""

    # ── Application ───────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True
    APP_TITLE: str = "NeuroProctor AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "AI-powered student face registration and impersonation detection service "
        "for the NeuroProctor exam integrity platform."
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Must match the React frontend origin exactly (no trailing slash).
    CORS_ORIGIN: str = "http://localhost:5173"

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGO_URI: str = "mongodb://localhost:27017/neuroproctor"
    MONGO_DB_NAME: str = "neuroproctor"

    # ── JWT ───────────────────────────────────────────────────────────────────
    # ACCESS_TOKEN_SECRET MUST be identical to the Express backend secret.
    # No default is provided so that a missing value raises an error at startup.
    ACCESS_TOKEN_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # ── Cloudinary ────────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_STUDENT_FOLDER: str = "neuroproctor/students"

    # ── InsightFace / ONNX ────────────────────────────────────────────────────
    INSIGHTFACE_MODEL_NAME: str = "buffalo_l"
    # ctx_id: 0 = first GPU device.  -1 forces CPU-only.
    INSIGHTFACE_CTX_ID: int = 0
    # Detection input size in pixels (square). 640 is the recommended default.
    INSIGHTFACE_DET_SIZE: int = 640

    # ── Image Validation ──────────────────────────────────────────────────────
    MAX_IMAGE_SIZE_MB: int = 5
    EMBEDDING_DIMENSION: int = 512

    # Allowed MIME types for uploaded images.
    # ClassVar tells Pydantic NOT to treat this as a settings field.
    ALLOWED_IMAGE_TYPES: ClassVar[list[str]] = [
        "image/jpeg",
        "image/jpg",
        "image/png",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,   # Env vars ARE case-sensitive on Linux
        extra="ignore",        # Silently ignore unknown env vars
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.

    lru_cache ensures the .env file is read only once across the entire
    application lifetime, making settings lookups effectively free.
    """
    return Settings()


# ---------------------------------------------------------------------------
# Module-level singleton — import directly for zero-overhead access.
# ---------------------------------------------------------------------------
settings: Settings = get_settings()
