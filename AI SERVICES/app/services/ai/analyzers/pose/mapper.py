"""Mapper for storing pose results in FrameContext."""

import logging
from typing import Dict

from app.services.ai.analyzers.pose.pose import PoseResult
from app.services.ai.pipeline.context import FrameContext

logger = logging.getLogger(__name__)


class PoseMapper:
    """Maps pose results to FrameContext."""
    
    def map(self, context: FrameContext, poses: list) -> FrameContext:
        """Store pose results in FrameContext.
        
        Args:
            context: FrameContext to update.
            poses: List of PoseResult with track IDs.
            
        Returns:
            Updated FrameContext with poses.
        """
        # Store poses as dictionary keyed by track_id
        context.poses = {
            pose.track_id: pose
            for pose in poses
        }
        
        return context
