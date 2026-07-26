"""Event emitter helper for common pipeline events."""

import logging
from typing import Any, Dict, Optional

from app.services.ai.monitoring.pipeline_logger import PipelineLogger

logger = logging.getLogger(__name__)


class EventEmitter:
    """Helper class for emitting common pipeline events.
    
    This class provides reusable methods for emitting standard
    pipeline events, reducing code duplication across modules.
    """
    
    def __init__(self, logger: PipelineLogger) -> None:
        """Initialize the event emitter.
        
        Args:
            logger: The pipeline logger instance.
        """
        self._logger = logger
    
    async def emit_info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an info event.
        
        Args:
            message: The message.
            data: Optional additional data.
        """
        logger.info("EventEmitter: Emitting info event - %s", message)
        await self._logger.info(message, emit_event="pipeline_info", data=data)
    
    async def emit_warning(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit a warning event.
        
        Args:
            message: The message.
            data: Optional additional data.
        """
        await self._logger.warning(message, emit_event="pipeline_warning", data=data)
    
    async def emit_error(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an error event.
        
        Args:
            message: The message.
            data: Optional additional data.
        """
        await self._logger.error(message, emit_event="pipeline_error", data=data)
    
    async def emit_stage_started(self, stage_name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit a stage started event.
        
        Args:
            stage_name: The name of the stage.
            data: Optional additional data.
        """
        event_data = data or {}
        event_data["stage"] = stage_name
        await self._logger.info(f"Stage started: {stage_name}", emit_event="stage_started", data=event_data)
    
    async def emit_stage_completed(self, stage_name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit a stage completed event.
        
        Args:
            stage_name: The name of the stage.
            data: Optional additional data.
        """
        event_data = data or {}
        event_data["stage"] = stage_name
        await self._logger.info(f"Stage completed: {stage_name}", emit_event="stage_completed", data=event_data)
    
    async def emit_pipeline_started(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit a pipeline started event.
        
        Args:
            data: Optional additional data.
        """
        await self._logger.info("Pipeline started", emit_event="pipeline_started", data=data)
    
    async def emit_pipeline_completed(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit a pipeline completed event.
        
        Args:
            data: Optional additional data.
        """
        await self._logger.info("Pipeline completed", emit_event="pipeline_completed", data=data)
    
    async def emit_pipeline_failed(self, error: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit a pipeline failed event.
        
        Args:
            error: The error message.
            data: Optional additional data.
        """
        event_data = data or {}
        event_data["error"] = error
        await self._logger.error(f"Pipeline failed: {error}", emit_event="pipeline_failed", data=event_data)
