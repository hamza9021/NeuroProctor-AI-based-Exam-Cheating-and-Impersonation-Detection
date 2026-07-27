"""DeepSORT tracking service."""

import logging
import time
from typing import List, Tuple

import numpy as np

from app.services.ai.monitoring.pipeline_logger import PipelineLogger
from app.services.ai.pipeline.context import Detection, FrameContext
from app.services.ai.trackers.deepsort.annotator import TrackAnnotator
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.constants import (
    EVENT_TRACKING_ANNOTATION_FAILED,
    EVENT_TRACKING_DETECTIONS_RECEIVED,
    EVENT_TRACKING_PERSON_DETECTIONS_FILTERED,
    EVENT_TRACKING_FRAME_COMPLETED,
    EVENT_TRACKING_UPDATE_COMPLETED,
    EVENT_TRACKING_UPDATE_STARTED,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_DETAILED,
    LOG_LEVEL_SUMMARY,
)
from app.services.ai.trackers.deepsort.loader import TrackerLoader
from app.services.ai.trackers.deepsort.mapper import TrackMapper
from app.services.ai.trackers.deepsort.monitor import TrackingMonitor
from app.services.ai.trackers.deepsort.parser import TrackParser
from app.services.ai.trackers.deepsort.tracker import Tracker
from app.services.ai.trackers.deepsort.validator import DetectionValidator

logger = logging.getLogger(__name__)


class DeepSORTService:
    """Service for DeepSORT tracking operations.
    
    Exposes one public method:
    track(context: FrameContext) -> FrameContext
    
    Coordinates:
    1. Validation
    2. Tracking
    3. Parsing
    4. Mapping
    5. Annotation
    """
    
    def __init__(self, config: DeepSORTConfig, pipeline_logger: PipelineLogger):
        """Initialize DeepSORT service.
        
        Args:
            config: DeepSORT configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._monitor = TrackingMonitor(pipeline_logger)
        self._loader = TrackerLoader(config, pipeline_logger)
        self._tracker = None
        self._validator = DetectionValidator()
        self._parser = TrackParser(self._monitor)
        self._mapper = TrackMapper()
        self._annotator = TrackAnnotator()
        self._initialized = False
        self._frame_count = 0
        self._last_annotation_error = None
        self._annotation_error_count = 0
    
    async def initialize(self):
        """Initialize the tracker.
        
        Loads the DeepSORT model and tracker.
        """
        if self._initialized:
            return
        
        logger.info("Initializing DeepSORT service")
        self._tracker = Tracker(
            await self._loader.load(),
            self._config,
        )
        self._initialized = True
        logger.info("DeepSORT service initialized")
    
    async def track(self, context: FrameContext) -> FrameContext:
        """Track persons in the frame.
        
        Args:
            context: FrameContext with detections.
            
        Returns:
            Updated FrameContext with tracks and annotations.
        """
        if not self._initialized:
            await self.initialize()
        
        self._frame_count += 1
        start_time = time.time()
        
        # Validate detections
        person_detections, stats = self._validator.validate(
            context.detections,
            self._config.detection_confidence_threshold,
        )
        
        await self._logger.info(
            f"YOLO detections received: {stats['total_detections']}",
            emit_event=EVENT_TRACKING_DETECTIONS_RECEIVED,
            data={"total_detections": stats["total_detections"]},
        )
        
        await self._logger.info(
            f"Person detections found: {stats['valid_person_detections']}",
            emit_event=EVENT_TRACKING_PERSON_DETECTIONS_FILTERED,
            data=stats,
        )
        
        if not person_detections:
            context.tracks = []
            return context
        
        # Prepare detections for tracker
        detections_for_tracker = self._prepare_detections(person_detections)
        
        # Update tracker
        await self._logger.info(
            "DeepSORT update started",
            emit_event=EVENT_TRACKING_UPDATE_STARTED,
        )
        
        raw_tracks = self._tracker.update(context.frame, detections_for_tracker)
        
        await self._logger.info(
            "DeepSORT update completed",
            emit_event=EVENT_TRACKING_UPDATE_COMPLETED,
        )
        
        # Parse tracks
        tracks = await self._parser.parse(raw_tracks)
        
        # Map detections to tracks
        context.detections, tracks = self._mapper.map_detections_to_tracks(
            context.detections,
            tracks,
        )
        
        # Update context
        context.tracks = tracks
        
        # Annotate frame (optional, preserve tracking if fails)
        original_frame = context.frame.copy()
        try:
            context.frame = self._annotator.annotate(context.frame, tracks)
            self._last_annotation_error = None
            self._annotation_error_count = 0
        except Exception as e:
            logger.warning(f"Annotation failed, preserving original frame: {e}")
            context.frame = original_frame
            
            # Log full traceback once for new errors
            if str(e) != str(self._last_annotation_error):
                logger.debug(f"Full annotation error traceback:", exc_info=True)
                self._last_annotation_error = str(e)
                self._annotation_error_count = 1
            else:
                self._annotation_error_count += 1
                logger.warning(f"Repeated annotation error (count: {self._annotation_error_count})")
            
            # Emit annotation failure event (rate-limited)
            if self._annotation_error_count == 1 or self._annotation_error_count % 10 == 0:
                await self._monitor.emit_tracking_warning(
                    f"Annotation failed: {str(e)}",
                    data={
                        "frame_number": context.frame_number,
                        "error_count": self._annotation_error_count,
                    },
                )
            
            # If annotation is mandatory, raise error
            if self._config.annotation_required:
                raise
        
        # Emit frame completion
        processing_time = (time.time() - start_time) * 1000
        await self._emit_frame_completion(context, processing_time)
        
        logger.debug(f"Tracking complete. Active tracks: {len(tracks)}")
        
        return context
    
    def _prepare_detections(
        self,
        detections: List[Detection],
    ) -> List[Tuple]:
        """Prepare detections for DeepSORT tracker.
        
        Args:
            detections: List of Detection objects.
            
        Returns:
            List of (bbox, confidence, class_id) tuples.
        """
        prepared = []
        for det in detections:
            prepared.append((det.bbox, det.confidence, 0))
        
        return prepared
    
    async def _emit_frame_completion(
        self,
        context: FrameContext,
        processing_time: float,
    ):
        """Emit frame completion event based on log level.
        
        Args:
            context: FrameContext.
            processing_time: Processing time in ms.
        """
        log_level = self._config.socket_log_detail_level
        frame_interval = self._config.frame_log_interval
        
        # Always emit for first frame, last frame, or on interval
        should_emit = (
            self._frame_count == 1
            or self._frame_count % frame_interval == 0
            or log_level == LOG_LEVEL_DEBUG
        )
        
        if not should_emit and log_level == LOG_LEVEL_SUMMARY:
            return
        
        # Count track states
        confirmed = sum(1 for t in context.tracks if t.is_confirmed)
        tentative = sum(1 for t in context.tracks if not t.is_confirmed)
        lost = sum(1 for t in context.tracks if t.time_since_update > 0)
        
        await self._logger.info(
            f"Frame {context.frame_number} tracking completed",
            emit_event=EVENT_TRACKING_FRAME_COMPLETED,
            data={
                "frame_number": context.frame_number,
                "active_tracks": len(context.tracks),
                "confirmed_tracks": confirmed,
                "tentative_tracks": tentative,
                "lost_tracks": lost,
                "processing_time_ms": round(processing_time, 2),
            },
        )
