"""Parser for DeepSORT tracker output."""

import logging
from typing import List

from app.services.ai.trackers.deepsort.constants import (
    EVENT_TRACK_CONFIRMED,
    EVENT_TRACK_CREATED,
    EVENT_TRACK_RECOVERED,
    EVENT_TRACK_TEMPORARILY_LOST,
    EVENT_TRACK_UPDATED,
)
from app.services.ai.trackers.deepsort.exceptions import TrackParsingError
from app.services.ai.trackers.deepsort.monitor import TrackingMonitor
from app.services.ai.trackers.deepsort.track import Track
from app.services.ai.trackers.deepsort.track_state_manager import TrackStateManager

logger = logging.getLogger(__name__)


class TrackParser:
    """Parses raw DeepSORT tracker output into Track objects.
    
    Converts raw tracker output into project Track models.
    Extracts track ID, bounding box, confirmation state, age, hits,
    time since update, detection confidence, class name, and center point.
    """
    
    def __init__(self, monitor: TrackingMonitor):
        """Initialize parser with monitor.
        
        Args:
            monitor: Tracking monitor for Socket.IO events.
        """
        self._monitor = monitor
        self._state_manager = TrackStateManager()
    
    async def parse(self, raw_tracks: List) -> List[Track]:
        """Parse raw tracker output into Track objects.
        
        Args:
            raw_tracks: Raw output from DeepSORT tracker.
            
        Returns:
            List of parsed Track objects.
        """
        tracks = []
        
        for track in raw_tracks:
            try:
                track_obj = await self._parse_single_track(track)
                tracks.append(track_obj)
            except Exception as e:
                logger.warning(f"Failed to parse track: {e}")
                continue
        
        return tracks
    
    async def _parse_single_track(self, raw_track) -> Track:
        """Parse a single raw track.
        
        Args:
            raw_track: Single raw track from centroid tracker (dict).
            
        Returns:
            Parsed Track object.
            
        Raises:
            TrackParsingError: If parsing fails.
        """
        try:
            # Extract track information from centroid tracker dict
            track_id = int(raw_track['track_id'])
            bbox = raw_track['bbox']
            centroid = raw_track['centroid']
            
            # Center point
            center = (float(centroid[0]), float(centroid[1]))
            
            # Confidence (default for centroid tracker)
            confidence = 0.8
            
            # Track state
            is_confirmed = raw_track['is_confirmed']
            age = raw_track['age']
            hits = raw_track['hits']
            time_since_update = raw_track['time_since_update']
            
            # Emit track lifecycle events
            await self._emit_track_event(
                track_id, is_confirmed, time_since_update, age, hits
            )
            
            # Class name (default to person for tracking)
            class_name = "person"
            
            return Track(
                track_id=track_id,
                bbox=(int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])),
                center=center,
                confidence=float(confidence),
                is_confirmed=is_confirmed,
                age=age,
                hits=hits,
                time_since_update=time_since_update,
                class_name=class_name,
            )
            
        except Exception as e:
            raise TrackParsingError(f"Failed to parse track: {e}") from e
    
    async def _emit_track_event(
        self,
        track_id: int,
        is_confirmed: bool,
        time_since_update: int,
        age: int,
        hits: int,
    ):
        """Emit appropriate track lifecycle event based on state transitions.
        
        Args:
            track_id: Track ID.
            is_confirmed: Whether track is confirmed.
            time_since_update: Time since last update.
            age: Track age.
            hits: Number of hits.
        """
        transitions = self._state_manager.update_state(
            track_id, is_confirmed, time_since_update, age, hits
        )
        
        if transitions["created"]:
            await self._monitor.emit_track_created(track_id)
        elif transitions["confirmed"]:
            await self._monitor.emit_track_confirmed(track_id)
        elif transitions["lost"]:
            await self._monitor.emit_track_temporarily_lost(track_id)
        elif transitions["recovered"]:
            await self._monitor.emit_track_recovered(track_id)
        elif transitions["updated"]:
            await self._monitor.emit_track_updated(track_id)
