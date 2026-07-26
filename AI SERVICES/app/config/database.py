"""
MongoDB connection management using Motor (async driver).

Design decisions:
  - The client is created ONCE during the FastAPI lifespan startup event
    and stored in module-level variables.  This means a single connection
    pool is shared across every request — no per-request reconnection.
  - Motor is non-blocking: all I/O is awaited on the asyncio event loop
    without blocking threads.
  - Indexes are created/verified at startup so they are never missing in
    production, even after a fresh database deployment.

Usage (in repositories):
    from app.config.database import get_database
    db = get_database()
    doc = await db["students"].find_one({"_id": some_id})
"""
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Module-level references — None until connect_to_mongo() is called.
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    """
    Initialise the Motor client and verify the connection with a ping.

    Called exactly once inside the FastAPI lifespan startup block.
    After this call, get_database() is safe to use anywhere.

    Raises:
        Exception: If MongoDB is unreachable within the serverSelectionTimeout.
    """
    global _client, _database

    logger.info("Connecting to MongoDB — URI: %s", settings.MONGO_URI)

    _client = AsyncIOMotorClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5_000,   # Fail fast if Mongo is down
        connectTimeoutMS=5_000,
        maxPoolSize=50,                   # Max concurrent connections
        minPoolSize=5,                    # Keep at least 5 connections alive
        retryWrites=True,
    )

    # Verify connectivity before accepting traffic
    await _client.admin.command("ping")
    logger.info("MongoDB ping successful.")

    _database = _client[settings.MONGO_DB_NAME]
    await _create_indexes()

    logger.info(
        "MongoDB connected — database: '%s'", settings.MONGO_DB_NAME
    )


async def close_mongo_connection() -> None:
    """
    Gracefully close the Motor connection pool.

    Called inside the FastAPI lifespan shutdown block.
    """
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection pool closed.")


async def _create_indexes() -> None:
    """
    Ensure required MongoDB indexes exist on the 'students' collection.

    Creating indexes with background=True means they are built without
    blocking existing reads/writes.  Calling this on every startup is safe
    because MongoDB is idempotent for index creation (it skips if exists).
    """
    students = _database["students"]

    # Unique constraints — prevent duplicate registration numbers and emails
    await students.create_index(
        [("registration_number", ASCENDING)],
        unique=True,
        background=True,
        name="idx_registration_number_unique",
    )
    await students.create_index(
        [("email", ASCENDING)],
        unique=True,
        background=True,
        name="idx_email_unique",
    )

    # Query optimisation — common filter/sort fields
    await students.create_index(
        [("full_name", ASCENDING)],
        background=True,
        name="idx_full_name",
    )
    await students.create_index(
        [("department", ASCENDING)],
        background=True,
        name="idx_department",
    )
    await students.create_index(
        [("is_active", ASCENDING)],
        background=True,
        name="idx_is_active",
    )
    await students.create_index(
        [("created_at", ASCENDING)],
        background=True,
        name="idx_created_at",
    )

    logger.info("MongoDB indexes created / verified on 'students' collection.")


def get_database() -> AsyncIOMotorDatabase:
    """
    Return the active Motor database instance.

    This function is used by all repository classes to access the database
    without holding a module-level reference to it themselves.

    Returns:
        AsyncIOMotorDatabase — the connected database.

    Raises:
        RuntimeError: If called before connect_to_mongo() has run.
    """
    if _database is None:
        raise RuntimeError(
            "Database is not initialised. "
            "Ensure connect_to_mongo() was awaited during application startup."
        )
    return _database
