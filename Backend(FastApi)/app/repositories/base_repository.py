"""
Generic async MongoDB base repository.

Provides reusable CRUD primitives (find, insert, update, delete, aggregate)
for any MongoDB collection.  Concrete repositories extend this class by
setting the class-level `collection_name` attribute and adding
domain-specific query methods.

Design decisions:
  - The database connection is retrieved lazily via get_database() so
    that repositories can be instantiated before the DB is connected.
  - All methods are async (Motor driver is fully non-blocking).
  - No ORM or ODM — raw dicts are returned from MongoDB queries so that
    callers retain full control over serialisation.
  - ID values are always handled as both str and ObjectId to prevent
    the common bug of mixing types in filter queries.
"""
import logging
from typing import Any, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config.database import get_database

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Async MongoDB repository base class.

    Subclasses must declare:
        collection_name: str = "your_collection"

    Example:
        class StudentRepository(BaseRepository):
            collection_name = "students"
    """

    collection_name: str = ""

    def __init__(self) -> None:
        if not self.collection_name:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define 'collection_name'."
            )

    # -------------------------------------------------------------------------
    # Database / collection accessors
    # -------------------------------------------------------------------------

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Return the active Motor database instance."""
        return get_database()

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Return the Motor collection for this repository."""
        return self.db[self.collection_name]

    # -------------------------------------------------------------------------
    # Read operations
    # -------------------------------------------------------------------------

    async def find_one(self, filter_: dict) -> Optional[dict]:
        """
        Return the first document matching *filter_*, or None.

        Args:
            filter_: MongoDB query filter dict.

        Returns:
            Raw document dict, or None if no match.
        """
        return await self.collection.find_one(filter_)

    async def find_by_id(self, document_id: str) -> Optional[dict]:
        """
        Return a document by its string ObjectId.

        Returns None if the string is not a valid ObjectId format or if
        no document with that ID exists.

        Args:
            document_id: 24-character hex string representation of ObjectId.

        Returns:
            Raw document dict, or None.
        """
        if not ObjectId.is_valid(document_id):
            logger.debug("find_by_id called with invalid ObjectId: '%s'", document_id)
            return None
        return await self.collection.find_one({"_id": ObjectId(document_id)})

    async def find_many(
        self,
        filter_: dict,
        skip: int = 0,
        limit: int = 20,
        sort: Optional[list[tuple[str, int]]] = None,
        projection: Optional[dict] = None,
    ) -> list[dict]:
        """
        Return a list of documents matching *filter_*.

        Args:
            filter_:    MongoDB query filter dict.
            skip:       Number of documents to skip (for pagination).
            limit:      Maximum number of documents to return.
            sort:       List of (field, direction) tuples (e.g. [("name", 1)]).
            projection: Optional field projection dict.

        Returns:
            List of raw document dicts (may be empty).
        """
        cursor = self.collection.find(filter_, projection).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=limit if limit > 0 else None)

    async def count(self, filter_: dict) -> int:
        """
        Count documents matching *filter_*.

        Args:
            filter_: MongoDB query filter dict.

        Returns:
            Integer count.
        """
        return await self.collection.count_documents(filter_)

    async def exists(self, filter_: dict) -> bool:
        """Return True if at least one document matches *filter_*."""
        return await self.count(filter_) > 0

    # -------------------------------------------------------------------------
    # Write operations
    # -------------------------------------------------------------------------

    async def insert_one(self, document: dict) -> str:
        """
        Insert a new document into the collection.

        Args:
            document: Dict to insert. Must NOT contain an `_id` key unless
                      you want to specify the ObjectId manually.

        Returns:
            String representation of the inserted document's ObjectId.
        """
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def update_one(self, filter_: dict, update: dict) -> bool:
        """
        Apply *update* to the first document matching *filter_*.

        Args:
            filter_: MongoDB filter to locate the target document.
            update:  MongoDB update expression (e.g. {"$set": {...}}).

        Returns:
            True if a document was matched and modified.
        """
        result = await self.collection.update_one(filter_, update)
        return result.modified_count > 0

    async def update_by_id(self, document_id: str, update: dict) -> bool:
        """
        Apply *update* to the document with the given ObjectId string.

        Args:
            document_id: 24-character hex string ObjectId.
            update:      MongoDB update expression.

        Returns:
            True if the document was matched and modified.
        """
        if not ObjectId.is_valid(document_id):
            return False
        return await self.update_one(
            {"_id": ObjectId(document_id)}, update
        )

    async def delete_one(self, filter_: dict) -> bool:
        """
        Delete the first document matching *filter_*.

        Args:
            filter_: MongoDB filter to locate the target document.

        Returns:
            True if a document was deleted.
        """
        result = await self.collection.delete_one(filter_)
        return result.deleted_count > 0

    async def delete_by_id(self, document_id: str) -> bool:
        """
        Hard-delete a document by its string ObjectId.

        Args:
            document_id: 24-character hex string ObjectId.

        Returns:
            True if the document was found and deleted.
        """
        if not ObjectId.is_valid(document_id):
            logger.debug(
                "delete_by_id called with invalid ObjectId: '%s'", document_id
            )
            return False
        return await self.delete_one({"_id": ObjectId(document_id)})

    # -------------------------------------------------------------------------
    # Aggregation
    # -------------------------------------------------------------------------

    async def aggregate(self, pipeline: list[dict[str, Any]]) -> list[dict]:
        """
        Execute a MongoDB aggregation pipeline.

        Args:
            pipeline: List of aggregation stage dicts.

        Returns:
            List of result dicts (may be empty).
        """
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
