"""
PipelineFactory - Factory for creating pipeline instances.

This module provides the PipelineFactory class which is responsible for
creating configured pipeline instances. It follows the Factory Pattern to
encapsulate pipeline creation logic and make it easy to add new pipeline types.

The factory enables dependency injection by accepting stage instances and
configuration parameters, ensuring pipelines are created with all required
dependencies.
"""

import logging
from typing import Dict, List, Optional

from app.services.ai.pipeline.base_pipeline import BasePipeline, PipelineStage
from app.services.ai.pipeline.live_pipeline import LivePipeline
from app.services.ai.pipeline.offline_pipeline import OfflinePipeline

logger = logging.getLogger(__name__)


class PipelineFactory:
    """
    Factory for creating configured pipeline instances.

    This factory provides a centralized way to create pipeline instances
. It handles the instantiation of different pipeline types with appropriate
    configuration, making it easy to add new pipeline types in the future.

    The factory follows the Open/Closed Principle - new pipeline types can
    be added by extending the factory without modifying existing code.

    Example:
        factory = PipelineFactory()
        
        # Create offline pipeline
        offline = factory.create_offline_pipeline(
            stages=[detector, tracker, analyzer],
            continue_on_error=False
        )
        
        # Create live pipeline
        live = factory.create_live_pipeline(
            stages=[detector, tracker],
            target_fps=30.0,
            skip_frames=True
        )
    """

    def create_offline_pipeline(
        self,
        stages: Optional[List[PipelineStage]] = None,
        continue_on_error: bool = False,
    ) -> OfflinePipeline:
        """
        Create an OfflinePipeline instance with the specified configuration.

        Args:
            stages: List of PipelineStage instances to register.
            continue_on_error: If True, continue processing remaining stages
                             even if one stage fails.

        Returns:
            Configured OfflinePipeline instance.
        """
        logger.info(
            "Creating OfflinePipeline with %d stages, continue_on_error=%s",
            len(stages) if stages else 0,
            continue_on_error,
        )
        return OfflinePipeline(
            stages=stages,
            continue_on_error=continue_on_error,
        )

    def create_live_pipeline(
        self,
        stages: Optional[List[PipelineStage]] = None,
        target_fps: Optional[float] = None,
        skip_frames: bool = False,
        continue_on_error: bool = True,
    ) -> LivePipeline:
        """
        Create a LivePipeline instance with the specified configuration.

        Args:
            stages: List of PipelineStage instances to register.
            target_fps: Target frames per second for real-time processing.
            skip_frames: If True, skip frames to maintain target_fps.
            continue_on_error: If True, continue processing remaining stages
                             even if one stage fails.

        Returns:
            Configured LivePipeline instance.
        """
        logger.info(
            "Creating LivePipeline with %d stages, target_fps=%s, skip_frames=%s, continue_on_error=%s",
            len(stages) if stages else 0,
            target_fps,
            skip_frames,
            continue_on_error,
        )
        return LivePipeline(
            stages=stages,
            target_fps=target_fps,
            skip_frames=skip_frames,
            continue_on_error=continue_on_error,
        )

    def create_pipeline(
        self,
        pipeline_type: str,
        stages: Optional[List[PipelineStage]] = None,
        **config,
    ) -> BasePipeline:
        """
        Create a pipeline instance by type name.

        This method provides a generic interface for creating any pipeline type,
        making it easy to add new pipeline types in the future.

        Args:
            pipeline_type: Type of pipeline to create ("offline" or "live").
            stages: List of PipelineStage instances to register.
            **config: Additional configuration parameters specific to the pipeline type.

        Returns:
            Configured pipeline instance.

        Raises:
            ValueError: If pipeline_type is not recognized.
        """
        pipeline_creators: Dict[str, callable] = {
            "offline": self.create_offline_pipeline,
            "live": self.create_live_pipeline,
        }

        creator = pipeline_creators.get(pipeline_type.lower())
        if not creator:
            raise ValueError(
                f"Unknown pipeline type: {pipeline_type}. "
                f"Available types: {list(pipeline_creators.keys())}"
            )

        logger.info("Creating pipeline of type '%s'", pipeline_type)
        return creator(stages=stages, **config)

    def create_from_config(
        self,
        config: Dict[str, any],
        stages: Optional[List[PipelineStage]] = None,
    ) -> BasePipeline:
        """
        Create a pipeline instance from a configuration dictionary.

        This method enables pipeline creation from external configuration
        files or database records, making the system more flexible.

        Args:
            config: Dictionary containing pipeline configuration with keys:
                   - type: Pipeline type ("offline" or "live")
                   - Additional keys specific to the pipeline type
            stages: List of PipelineStage instances to register.

        Returns:
            Configured pipeline instance.

        Raises:
            ValueError: If configuration is invalid or pipeline type not recognized.
        """
        pipeline_type = config.get("type")
        if not pipeline_type:
            raise ValueError("Configuration must include 'type' field")

        # Remove 'type' from config as it's used for routing
        pipeline_config = {k: v for k, v in config.items() if k != "type"}

        logger.info(
            "Creating pipeline from config: type=%s, config=%s",
            pipeline_type,
            pipeline_config,
        )
        return self.create_pipeline(pipeline_type, stages=stages, **pipeline_config)
