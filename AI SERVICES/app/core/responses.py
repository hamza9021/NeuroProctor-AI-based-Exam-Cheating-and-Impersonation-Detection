"""
Standardised JSON response builders.

Every API response — success or error — follows one of two envelopes:

    Success:
        {
            "success": true,
            "message": "Human-readable description",
            "data": { ... }  or  null
        }

    Error (produced by exception handlers in core/exceptions.py):
        {
            "success": false,
            "message": "Human-readable description",
            "errors": [ "Optional detail messages …" ]
        }

    Paginated list (success variant):
        {
            "success": true,
            "message": "...",
            "data": {
                "students": [...],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "limit": 10,
                    "total_pages": 10,
                    "has_next": true,
                    "has_prev": false
                }
            }
        }

Using JSONResponse directly (instead of Pydantic response models) gives us
full control over serialisation, particularly for BSON types and datetime.
"""
from typing import Any

from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success.",
    status_code: int = 200,
) -> JSONResponse:
    """
    Build a standardised success JSON response.

    Args:
        data:        Serialisable payload to nest under the "data" key.
                     Pass None for operations that return no data (e.g. delete).
        message:     Human-readable success message shown to the client.
        status_code: HTTP status code. Defaults to 200.

    Returns:
        JSONResponse with the standard success envelope.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )


def paginated_response(
    data: list[Any],
    total: int,
    page: int,
    limit: int,
    message: str = "Success.",
) -> JSONResponse:
    """
    Build a standardised paginated list response.

    Computes pagination metadata automatically from the provided counts.

    Args:
        data:    Serialised list of items for the current page.
        total:   Total number of matching documents across all pages.
        page:    Current page number (1-indexed).
        limit:   Number of items per page.
        message: Human-readable success message.

    Returns:
        JSONResponse containing the items and pagination metadata.
    """
    total_pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": message,
            "data": {
                "students": data,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            },
        },
    )
