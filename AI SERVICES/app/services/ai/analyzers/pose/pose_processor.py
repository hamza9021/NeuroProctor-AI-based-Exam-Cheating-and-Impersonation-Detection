"""Pose processing logic."""

import logging

from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.analyzers.pose.annotator import PoseAnnotator
from app.services.ai.analyzers.pose.associator import PoseAssociator
from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.estimator import PoseEstimator
from app.services.ai.analyzers.pose.frame_emitter import FrameEmitter
from app.services.ai.analyzers.pose.mapper import PoseMapper
from app.services.ai.analyzers.pose.parser import PoseParser
from app.services.ai.analyzers.pose.pose_inference import PoseInference
from app.services.ai.analyzers.pose.validator import PoseValidator

logger = logging.getLogger(__name__)


class PoseProcessor:
    """Processes pose estimation for frames."""
    
    def __init__(self, config: YoloPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize processor with configuration.
        
        Args:
            config: Pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._inference = PoseInference(config, pipeline_logger)
        self._mapper = PoseMapper()
        self._annotator = PoseAnnotator(config.keypoint_confidence)
        self._frame_emitter = FrameEmitter(config, pipeline_logger)
        self._frame_count = 0
    
    def initialize(self, model, config: YoloPoseConfig):
        """Initialize estimator with loaded model.
        
        Args:
            model: Loaded YOLO pose model.
            config: Pose configuration.
        """
        self._inference.initialize(model, config)
    
    async def process(self, context: FrameContext) -> FrameContext:
        """Process pose estimation for frame.
        
        Args:
            context: FrameContext with tracks.
            
        Returns:
            Updated FrameContext with poses and annotations.
        """
        self._frame_count += 1
        
        # Run inference and get poses
        poses = await self._inference.infer(context)
        
        logger.info(f"Frame {context.frame_number}: Got {len(poses)} poses from inference")
        
        # Map to context
        context = self._mapper.map(context, poses)
        
        # Annotate frame
        context.frame = self._annotator.annotate(context.frame, poses)
        
        logger.info(f"Frame {context.frame_number}: Annotated frame with {len(poses)} poses")
        
        # Emit frame completion
        await self._frame_emitter.emit_completion(context, self._frame_count)
        
        logger.debug(f"Pose estimation complete. Valid poses: {len(poses)}")
        
        return context
