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
    - PipelineManager: Stage registration and execution management
    - PipelineFactory: Factory for creating pipeline instances
"""

from app.services.ai.pipeline.base import BasePipeline
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.pipeline.factory import PipelineFactory
from app.services.ai.pipeline.interfaces import PipelineStage
from app.services.ai.pipeline.manager import PipelineManager
from app.services.ai.pipeline.offline import OfflinePipeline

__all__ = [
    "FrameContext",
    "PipelineStage",
    "BasePipeline",
    "OfflinePipeline",
    "PipelineManager",
    "PipelineFactory",
]
