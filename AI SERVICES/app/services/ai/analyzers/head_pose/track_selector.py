"""Track selector for head pose estimation."""

from app.services.ai.pipeline.context import FrameContext


class TrackSelector:
    """Selects eligible tracks for head pose estimation."""
    
    def select(self, context: FrameContext) -> list:
        """Select eligible tracks for head pose estimation.
        
        Args:
            context: FrameContext with tracks.
            
        Returns:
            List of eligible tracks.
        """
        eligible = []
        for track in context.tracks:
            if hasattr(track, "is_confirmed") and track.is_confirmed:
                if hasattr(track, "track_id") and track.track_id >= 0:
                    if hasattr(track, "bbox") and track.bbox:
                        eligible.append(track)
        return eligible
