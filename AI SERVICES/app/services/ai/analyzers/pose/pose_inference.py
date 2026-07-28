"""Pose inference with parsing and association."""

import logging

from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.analyzers.pose.associator import PoseAssociator
from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.constants import (
    EVENT_POSE_TRACKS_RECEIVED,
)
from app.services.ai.analyzers.pose.estimator import PoseEstimator
from app.services.ai.analyzers.pose.pose_pipeline import PosePipeline

logger = logging.getLogger(__name__)


class PoseInference:
    """Handles pose inference, parsing, validation, and association."""
    
    def __init__(self, config: YoloPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize inference with configuration.
        
        Args:
            config: Pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._estimator = None
        self._pipeline = PosePipeline(config, pipeline_logger)
    
    def initialize(self, model, config: YoloPoseConfig):
        """Initialize estimator with loaded model.
        
        Args:
            model: Loaded YOLO pose model.
            config: Pose configuration.
        """
        self._estimator = PoseEstimator(model, config)
    
    async def infer(self, context: FrameContext):
        """Run full inference pipeline.
        
        Args:
            context: FrameContext with tracks.
            
        Returns:
            List of associated PoseResult objects.
        """
        # Check for eligible tracks
        eligible_tracks = [
            t for t in context.tracks
            if t.is_confirmed and t.time_since_update < 10
        ]
        
        logger.info(f"Eligible tracks for pose: {len(eligible_tracks)}")
        
        await self._logger.info(
            f"Confirmed DeepSORT tracks received: {len(eligible_tracks)}",
            emit_event=EVENT_POSE_TRACKS_RECEIVED,
            data={"track_count": len(eligible_tracks)},
        )
        
        if not eligible_tracks:
            logger.info("No eligible tracks, skipping pose inference")
            return []
        
        # Run pose inference
        raw_results = self._estimator.estimate(context.frame)
        logger.info(f"Raw pose results count: {len(raw_results)}")
        
        # Run pipeline
        poses = await self._pipeline.process(raw_results, eligible_tracks, context)
        logger.info(f"Associated poses: {len(poses)}")
        
        return poses
