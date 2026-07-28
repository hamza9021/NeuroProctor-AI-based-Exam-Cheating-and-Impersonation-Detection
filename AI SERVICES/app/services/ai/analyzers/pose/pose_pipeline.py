"""Pose pipeline for parsing, validation, and association."""

import logging

from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.analyzers.pose.associator import PoseAssociator
from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.constants import (
    EVENT_POSE_CANDIDATES_PARSED,
    EVENT_POSE_CANDIDATES_VALIDATED,
    EVENT_POSE_INFERENCE_STARTED,
    EVENT_POSE_INFERENCE_COMPLETED,
    EVENT_POSE_MAPPING_COMPLETED,
)
from app.services.ai.analyzers.pose.parser import PoseParser
from app.services.ai.analyzers.pose.validator import PoseValidator

logger = logging.getLogger(__name__)


class PosePipeline:
    """Handles pose parsing, validation, and association."""
    
    def __init__(self, config: YoloPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize pipeline with configuration.
        
        Args:
            config: Pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._parser = PoseParser()
        self._validator = PoseValidator(config)
        self._associator = PoseAssociator(config)
    
    async def process(self, raw_results, eligible_tracks, context: FrameContext):
        """Process raw results through pipeline.
        
        Args:
            raw_results: Raw YOLO pose results.
            eligible_tracks: List of eligible tracks.
            context: FrameContext.
            
        Returns:
            List of associated PoseResult objects.
        """
        # Emit inference events
        await self._logger.info(
            "Pose inference started",
            emit_event=EVENT_POSE_INFERENCE_STARTED,
        )
        
        await self._logger.info(
            "Pose inference completed",
            emit_event=EVENT_POSE_INFERENCE_COMPLETED,
        )
        
        # Parse results
        candidates = self._parser.parse(raw_results)
        
        await self._logger.info(
            f"Raw pose candidates detected: {len(candidates)}",
            emit_event=EVENT_POSE_CANDIDATES_PARSED,
            data={"candidate_count": len(candidates)},
        )
        
        # Validate candidates
        h, w = context.frame.shape[:2]
        valid_candidates = self._validator.validate(candidates, w, h)
        
        await self._logger.info(
            f"Valid pose candidates: {len(valid_candidates)}",
            emit_event=EVENT_POSE_CANDIDATES_VALIDATED,
            data={"valid_count": len(valid_candidates)},
        )
        
        # Associate with tracks
        poses = self._associator.associate(eligible_tracks, valid_candidates)
        
        await self._logger.info(
            "Pose data stored in context",
            emit_event=EVENT_POSE_MAPPING_COMPLETED,
        )
        
        return poses
