"""Monitor for DeepSORT tracking events."""

import logging
from typing import Dict, Any

from app.services.ai.monitoring.pipeline_logger import PipelineLogger
from app.services.ai.trackers.deepsort.constants import (
    EVENT_TRACK_CONFIRMED,
    EVENT_TRACK_CREATED,
    EVENT_TRACK_RECOVERED,
    EVENT_TRACK_REMOVED,
    EVENT_TRACK_TEMPORARILY_LOST,
    EVENT_TRACK_UPDATED,
    EVENT_TRACKING_FAILED,
    EVENT_TRACKING_WARNING,
)

logger = logging.getLogger(__name__)


class TrackingMonitor:
    """Adapter for DeepSORT Socket.IO monitoring.
    
    Reuses existing Socket Manager, EventEmitter, and Pipeline Logger.
    Emits tracking lifecycle events with proper room isolation.
    """
    
    def __init__(self, pipeline_logger: PipelineLogger):
        """Initialize monitor with pipeline logger.
        
        Args:
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._logger = pipeline_logger
    
    async def emit_track_created(self, track_id: int):
        """Emit track created event.
        
        Args:
            track_id: Track ID.
        """
        await self._logger.info(
            f"Track #{track_id} created",
            emit_event=EVENT_TRACK_CREATED,
            data={"track_id": track_id},
        )
    
    async def emit_track_confirmed(self, track_id: int):
        """Emit track confirmed event.
        
        Args:
            track_id: Track ID.
        """
        await self._logger.info(
            f"Track #{track_id} confirmed",
            emit_event=EVENT_TRACK_CONFIRMED,
            data={"track_id": track_id},
        )
    
    async def emit_track_updated(self, track_id: int):
        """Emit track updated event.
        
        Args:
            track_id: Track ID.
        """
        await self._logger.info(
            f"Track #{track_id} updated",
            emit_event=EVENT_TRACK_UPDATED,
            data={"track_id": track_id},
        )
    
    async def emit_track_temporarily_lost(self, track_id: int):
        """Emit track temporarily lost event.
        
        Args:
            track_id: Track ID.
        """
        await self._logger.warning(
            f"Track #{track_id} temporarily lost",
            emit_event=EVENT_TRACK_TEMPORARILY_LOST,
            data={"track_id": track_id},
        )
    
    async def emit_track_recovered(self, track_id: int):
        """Emit track recovered event.
        
        Args:
            track_id: Track ID.
        """
        await self._logger.info(
            f"Track #{track_id} recovered",
            emit_event=EVENT_TRACK_RECOVERED,
            data={"track_id": track_id},
        )
    
    async def emit_track_removed(self, track_id: int):
        """Emit track removed event.
        
        Args:
            track_id: Track ID.
        """
        await self._logger.info(
            f"Track #{track_id} removed",
            emit_event=EVENT_TRACK_REMOVED,
            data={"track_id": track_id},
        )
    
    async def emit_tracking_warning(self, message: str, data: Dict[str, Any] = None):
        """Emit tracking warning event.
        
        Args:
            message: Warning message.
            data: Optional event data.
        """
        await self._logger.warning(
            message,
            emit_event=EVENT_TRACKING_WARNING,
            data=data or {},
        )
    
    async def emit_tracking_failed(self, message: str, data: Dict[str, Any] = None):
        """Emit tracking failed event.
        
        Args:
            message: Error message.
            data: Optional event data.
        """
        await self._logger.error(
            message,
            emit_event=EVENT_TRACKING_FAILED,
            data=data or {},
        )
