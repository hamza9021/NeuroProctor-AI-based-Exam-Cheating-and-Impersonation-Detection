"""Service initializer for head pose estimation."""

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.cropper import FaceCropper
from app.services.ai.analyzers.head_pose.estimator import HeadPoseEstimator
from app.services.ai.analyzers.head_pose.face_locator import FaceLocator
from app.services.ai.analyzers.head_pose.loader import HeadPoseModelLoader
from app.services.ai.analyzers.head_pose.mapper import HeadPoseMapper
from app.services.ai.analyzers.head_pose.monitor import HeadPoseMonitor
from app.services.ai.analyzers.head_pose.parser import HeadPoseParser
from app.services.ai.analyzers.head_pose.track_processor import TrackProcessor
from app.services.ai.analyzers.head_pose.track_selector import TrackSelector
from app.services.ai.analyzers.head_pose.validator import HeadPoseValidator
from app.services.ai.monitoring import PipelineLogger


class ServiceInitializer:
    """Initializes head pose service components."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize service initializer.
        
        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._monitor = HeadPoseMonitor(pipeline_logger)
        self._locator = FaceLocator(config, pipeline_logger)
        self._cropper = FaceCropper(config, pipeline_logger)
        self._parser = HeadPoseParser(pipeline_logger)
        self._validator = HeadPoseValidator(config, pipeline_logger)
        self._mapper = HeadPoseMapper(pipeline_logger)
        self._track_selector = TrackSelector()
    
    async def initialize_components(self):
        """Initialize model and estimator.
        
        Returns:
            Tuple of (model, estimator, track_processor).
        """
        loader = HeadPoseModelLoader(self._config, self._logger)
        model = await loader.load()
        estimator = HeadPoseEstimator(model, self._config, self._logger)
        track_processor = TrackProcessor(
            self._locator, self._cropper, estimator,
            self._parser, self._validator
        )
        return model, estimator, track_processor
    
    def get_components(self):
        """Get initialized components.
        
        Returns:
            Dictionary of components.
        """
        return {
            "monitor": self._monitor,
            "locator": self._locator,
            "cropper": self._cropper,
            "parser": self._parser,
            "validator": self._validator,
            "mapper": self._mapper,
            "track_selector": self._track_selector,
        }
