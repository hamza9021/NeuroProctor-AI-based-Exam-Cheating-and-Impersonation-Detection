"""
AI Pipeline Package.

This package provides a modular, extensible framework for building
AI processing pipelines for video analysis and cheating detection.

The framework follows the Open/Closed Principle - new pipeline stages
can be added without modifying existing pipeline code.

Components:
    - FrameContext: Data container for frame information
    - PipelineStage: Interface for all processing stages
    - BasePipeline: Abstract base class for pipeline implementations
    - OfflinePipeline: Pipeline for pre-recorded video processing
    - LivePipeline: Pipeline for real-time video processing
    - PipelineManager: Stage registration and execution management
    - PipelineFactory: Factory for creating pipeline instances
"""

from app.services.ai.pipeline.base_pipeline import BasePipeline, PipelineStage
from app.services.ai.pipeline.frame_context import FrameContext
from app.services.ai.pipeline.live_pipeline import LivePipeline
from app.services.ai.pipeline.offline_pipeline import OfflinePipeline
from app.services.ai.pipeline.pipeline_factory import PipelineFactory
from app.services.ai.pipeline.pipeline_manager import PipelineManager

__all__ = [
    "FrameContext",
    "PipelineStage",
    "BasePipeline",
    "OfflinePipeline",
    "LivePipeline",
    "PipelineManager",
    "PipelineFactory",
]
