"""Batch processor for multiple tracks."""

import logging

from app.services.ai.analyzers.head_pose.monitor import HeadPoseMonitor


class BatchProcessor:
    """Processes multiple tracks in batch."""
    
    def __init__(self, monitor: HeadPoseMonitor):
        """Initialize batch processor.
        
        Args:
            monitor: Head pose monitor for warnings.
        """
        self._monitor = monitor
    
    async def process(self, context, eligible_tracks: list, track_processor) -> list:
        """Process all eligible tracks.
        
        Args:
            context: FrameContext.
            eligible_tracks: List of eligible tracks.
            track_processor: Track processor instance.
            
        Returns:
            List of head pose results.
        """
        results = []
        
        for track in eligible_tracks:
            try:
                result = await track_processor.process(context, track)
                if result:
                    results.append(result)
            except Exception as e:
                logging.warning(f"Failed to process Track #{track.track_id}: {e}")
                await self._monitor.emit_warning(
                    f"Track #{track.track_id} failed: {str(e)}",
                    data={"track_id": track.track_id},
                )
        
        return results
