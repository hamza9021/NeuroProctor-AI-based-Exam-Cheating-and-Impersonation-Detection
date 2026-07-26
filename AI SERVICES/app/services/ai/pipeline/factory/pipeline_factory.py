"""Factory for creating configured pipeline instances."""

import logging

from app.services.ai.pipeline.base import BasePipeline
from app.services.ai.pipeline.offline import OfflinePipeline

logger = logging.getLogger(__name__)


class PipelineFactory:
    """Factory for creating and configuring pipeline instances.
    
    This factory provides a centralized way to create pipelines,
    making it easy to add new pipeline types in the future.
    """
    
    @staticmethod
    def create_offline_pipeline() -> OfflinePipeline:
        """Create an offline pipeline instance.
        
        Returns:
            A configured OfflinePipeline instance.
        """
        pipeline = OfflinePipeline()
        logger.info("Created OfflinePipeline")
        return pipeline
    
    @staticmethod
    def create_pipeline(pipeline_type: str) -> BasePipeline:
        """Create a pipeline by type.
        
        Args:
            pipeline_type: The type of pipeline to create.
                          Currently supports: "offline"
        
        Returns:
            A configured pipeline instance.
            
        Raises:
            ValueError: If the pipeline type is not supported.
        """
        if pipeline_type == "offline":
            return PipelineFactory.create_offline_pipeline()
        
        raise ValueError(f"Unsupported pipeline type: {pipeline_type}")
