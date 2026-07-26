"""
ObjectId utility for Pydantic v2 + MongoDB BSON compatibility.

PyObjectId wraps bson.ObjectId into a Pydantic-compatible annotated type
that automatically serialises to a plain string in JSON responses and
deserialises from a string in API inputs.

Used by all MongoDB document models (app/models/) so that `_id` fields
are transparently converted between ObjectId (in-DB) and str (in-JSON).
"""
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema


def validate_object_id(value: Any) -> ObjectId:
    """
    Coerce *value* to a bson.ObjectId.

    Accepts:
        - An existing ObjectId (passed through unchanged).
        - A 24-character hex string that is a valid ObjectId.

    Raises:
        ValueError: If *value* cannot be converted.
    """
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    raise ValueError(f"Invalid ObjectId value: {value!r}")


def serialize_object_id(value: ObjectId) -> str:
    """Serialise a bson.ObjectId to its hex string representation."""
    return str(value)


# ---------------------------------------------------------------------------
# PyObjectId — Annotated type used in Pydantic v2 models
# ---------------------------------------------------------------------------
# BeforeValidator  : runs validate_object_id() before Pydantic's own parsing.
# PlainSerializer  : converts ObjectId → str when .model_dump(mode="json") is
#                    called (i.e. for API responses and JSON serialisation).
# WithJsonSchema   : tells OpenAPI/Swagger that this field is a plain string.
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(serialize_object_id, return_type=str),
    WithJsonSchema({"type": "string", "example": "64b1f3a2c9e77b001f4d5e8a"}, mode="serialization"),
]


# ---------------------------------------------------------------------------
# Standalone helpers
# ---------------------------------------------------------------------------

def str_to_objectid(value: str) -> ObjectId:
    """
    Convert a hex string to a bson.ObjectId.

    Args:
        value: 24-character hex string.

    Returns:
        bson.ObjectId

    Raises:
        ValueError: If *value* is not a valid ObjectId string.
    """
    if not ObjectId.is_valid(value):
        raise ValueError(f"'{value}' is not a valid ObjectId string.")
    return ObjectId(value)


def objectid_to_str(value: ObjectId) -> str:
    """Convert a bson.ObjectId to its hex string representation."""
    return str(value)
