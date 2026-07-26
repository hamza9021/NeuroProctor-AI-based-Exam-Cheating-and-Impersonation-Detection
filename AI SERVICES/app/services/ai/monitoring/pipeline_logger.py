"""Pipeline logger for centralized logging and Socket.IO emission."""

import logging
from typing import Any, Dict, Optional

from app.services.ai.monitoring.socket_manager import socket_manager

logger = logging.getLogger(__name__)


class PipelineLogger:
    """Centralized logger for pipeline events.
    
    This class handles logging to console, file, and Socket.IO.
    It prevents duplication of logging logic across modules.
    """
    
    def __init__(self, session_id: Optional[str] = None) -> None:
        """Initialize the pipeline logger.
        
        Args:
            session_id: Optional session ID for room-based broadcasting.
        """
        self._session_id = session_id
        logger.debug("PipelineLogger created for session: %s", session_id)
    
    async def info(self, message: str, emit_event: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message.
        
        Args:
            message: The log message.
            emit_event: Optional Socket.IO event name to emit.
            data: Optional data to emit with the event.
        """
        logger.info(message)
        if emit_event:
            await self._emit(emit_event, data or {"message": message})
    
    async def warning(self, message: str, emit_event: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message.
        
        Args:
            message: The log message.
            emit_event: Optional Socket.IO event name to emit.
            data: Optional data to emit with the event.
        """
        logger.warning(message)
        if emit_event:
            await self._emit(emit_event, data or {"message": message})
    
    async def error(self, message: str, emit_event: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message.
        
        Args:
            message: The log message.
            emit_event: Optional Socket.IO event name to emit.
            data: Optional data to emit with the event.
        """
        logger.error(message)
        if emit_event:
            await self._emit(emit_event, data or {"message": message})
    
    async def _emit(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event via Socket.IO.
        
        Args:
            event: The event name.
            data: The event data.
        """
        if self._session_id:
            data["session_id"] = self._session_id
        # Use async emit properly
        try:
            await socket_manager.emit(event, data, room=None)
            logger.info("Successfully emitted Socket.IO event: %s", event)
        except Exception as e:
            logger.error("Failed to emit Socket.IO event: %s", e)
