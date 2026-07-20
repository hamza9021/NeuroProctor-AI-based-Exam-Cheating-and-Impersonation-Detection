"""
Health check routes.

Provides a public, unauthenticated endpoint for:
  - Container liveness probes (Kubernetes, Docker HEALTHCHECK)
  - Load balancer health checks
  - Monitoring systems (Prometheus, UptimeRobot, etc.)

No authentication required — health endpoints must remain accessible
even when JWT infrastructure is unavailable.
"""
import logging

from fastapi import APIRouter

from app.config.database import get_database
from app.core.responses import success_response
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Service health check",
    description=(
        "Returns the health status of the NeuroProctor AI backend and its "
        "dependencies (MongoDB, InsightFace model). No authentication required."
    ),
)
async def health_check():
    """
    Liveness and readiness probe for the AI backend.

    Checks:
      - FastAPI service is running and handling requests.
      - MongoDB connection is alive (ping command).
      - InsightFace model is loaded and ready.

    Returns:
        200 OK — Service and all components are healthy.
        200 OK — Service is running but a component is degraded
                 (still returns 200 to avoid false-positive container restarts;
                  the component status field indicates the issue).
    """
    # Check MongoDB connectivity
    db_status = "healthy"
    try:
        db = get_database()
        await db.command("ping")
    except Exception as exc:
        logger.warning("Health check — MongoDB ping failed: %s", exc)
        db_status = "unhealthy"

    # Check InsightFace model status (no I/O needed — just check the flag)
    model_status = "operational" if embedding_service._initialized else "not_loaded"

    return success_response(
        data={
            "service": "NeuroProctor AI Backend",
            "version": "1.0.0",
            "status": "healthy",
            "components": {
                "database": db_status,
                "face_recognition_model": model_status,
            },
        },
        message="Service is running and accepting requests.",
    )
