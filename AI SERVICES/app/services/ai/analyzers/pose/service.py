"""YOLO pose estimation service."""

import logging

from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.analyzers.pose.annotator import PoseAnnotator
from app.services.ai.analyzers.pose.associator import PoseAssociator
from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.estimator import PoseEstimator
from app.services.ai.analyzers.pose.frame_emitter import FrameEmitter
from app.services.ai.analyzers.pose.loader import PoseModelLoader
from app.services.ai.analyzers.pose.mapper import PoseMapper
from app.services.ai.analyzers.pose.monitor import PoseMonitor
from app.services.ai.analyzers.pose.parser import PoseParser
from app.services.ai.analyzers.pose.pose_processor import PoseProcessor
from app.services.ai.analyzers.pose.validator import PoseValidator

logger = logging.getLogger(__name__)


class YoloPoseService:
    """Service for YOLO pose estimation operations."""
    
    def __init__(self, config: YoloPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize pose service.
        
        Args:
            config: Pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._monitor = PoseMonitor(pipeline_logger)
        self._loader = PoseModelLoader(config, pipeline_logger)
        self._processor = PoseProcessor(config, pipeline_logger)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the pose model."""
        if self._initialized:
            return
        
        logger.info("Initializing YOLO pose service")
        model = await self._loader.load()
        self._processor.initialize(model, self._config)
        self._initialized = True
        logger.info("YOLO pose service initialized")
    
    async def estimate(self, context: FrameContext) -> FrameContext:
        """Estimate poses in the frame.
        
        Args:
            context: FrameContext with tracks.
            
        Returns:
            Updated FrameContext with poses and annotations.
        """
        if not self._initialized:
            await self.initialize()
        
        return await self._processor.process(context)
