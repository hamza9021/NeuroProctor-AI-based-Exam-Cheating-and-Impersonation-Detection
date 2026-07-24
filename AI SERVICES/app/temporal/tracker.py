"""
Event tracker for temporal smoothing.

This module tracks events over time, managing active events,
detecting event continuity, and handling event merging.
"""

from typing import Dict, Optional, List
from app.temporal.temporal_event import TemporalEvent, EventState
from app.temporal.state import EventStateManager
from app.events.event import ExamEvent
from app.utils.logger import get_logger


class EventTracker:
    """
    Tracks events over time for temporal smoothing.
    
    This class maintains active events, handles event continuity
    (allowing temporary detection loss), and manages event lifecycle.
    """
    
    def __init__(self, max_missing_frames: int = 5):
        """
        Initialize event tracker.
        
        Args:
            max_missing_frames: Maximum frames an event can be missing
                               before being considered ended
        """
        self.logger = get_logger(__name__)
        self.state_manager = EventStateManager()
        self.max_missing_frames = max_missing_frames
        
        # Active events keyed by event type
        self.active_events: Dict[str, TemporalEvent] = {}
        
        # Track missing frame counts for each event type
        self.missing_frame_counts: Dict[str, int] = {}
        
        # Statistics
        self.discarded_count = 0
        self.merged_count = 0
    
    def process_frame_events(
        self,
        frame_events: List[ExamEvent],
        frame_number: int,
        timestamp: float,
    ) -> List[TemporalEvent]:
        """
        Process events for a single frame.
        
        Args:
            frame_events: List of events from rule engine for this frame
            frame_number: Current frame number
            timestamp: Current timestamp
            
        Returns:
            List of newly ended events
        """
        ended_events = []
        
        # Get event types present in this frame
        present_event_types = {e.event_type.value for e in frame_events}
        
        # Update existing active events
        for event_type, event in list(self.active_events.items()):
            if event_type in present_event_types:
                # Event is still present, update it
                frame_event = next(
                    e for e in frame_events if e.event_type.value == event_type
                )
                self.state_manager.update_event(event, frame_event.confidence)
                self.missing_frame_counts[event_type] = 0
            else:
                # Event is missing, increment counter
                self.missing_frame_counts[event_type] += 1
                
                # Check if event should be ended
                if self.missing_frame_counts[event_type] >= self.max_missing_frames:
                    event = self.active_events.pop(event_type)
                    self.missing_frame_counts.pop(event_type)
                    self.state_manager.end_event(event, frame_number, timestamp)
                    ended_events.append(event)
        
        # Create new events for newly detected event types
        for event in frame_events:
            event_type = event.event_type.value
            if event_type not in self.active_events:
                new_event = self.state_manager.create_event(
                    event_type=event_type,
                    frame_number=frame_number,
                    timestamp=timestamp,
                    confidence=event.confidence,
                    metadata=event.metadata,
                )
                self.state_manager.activate_event(new_event)
                self.active_events[event_type] = new_event
                self.missing_frame_counts[event_type] = 0
        
        return ended_events
    
    def end_all_events(self, frame_number: int, timestamp: float) -> List[TemporalEvent]:
        """
        End all currently active events.
        
        Args:
            frame_number: Current frame number
            timestamp: Current timestamp
            
        Returns:
            List of ended events
        """
        ended_events = []
        
        for event_type, event in list(self.active_events.items()):
            event = self.active_events.pop(event_type)
            self.missing_frame_counts.pop(event_type, None)
            self.state_manager.end_event(event, frame_number, timestamp)
            ended_events.append(event)
        
        return ended_events
    
    def get_active_events(self) -> List[TemporalEvent]:
        """
        Get all currently active events.
        
        Returns:
            List of active events
        """
        return list(self.active_events.values())
    
    def discard_short_event(self, event: TemporalEvent, min_duration: float) -> bool:
        """
        Discard event if duration is below threshold.
        
        Args:
            event: Event to check
            min_duration: Minimum duration threshold in seconds
            
        Returns:
            True if event was discarded
        """
        if event.duration < min_duration:
            self.state_manager.discard_event(event, f"duration {event.duration:.2f}s < {min_duration:.2f}s")
            self.discarded_count += 1
            return True
        return False
    
    def merge_consecutive_events(
        self,
        events: List[TemporalEvent],
        merge_gap: float,
    ) -> List[TemporalEvent]:
        """
        Merge consecutive events of the same type if gap is small.
        
        Args:
            events: List of events to merge
            merge_gap: Maximum time gap between events to merge (seconds)
            
        Returns:
            List of merged events
        """
        if not events:
            return events
        
        # Sort by start time
        sorted_events = sorted(events, key=lambda e: e.start_time)
        
        merged = []
        current = sorted_events[0]
        
        for next_event in sorted_events[1:]:
            # Check if same type and within merge gap
            if (current.event_type == next_event.event_type and
                next_event.start_time - current.end_time <= merge_gap):
                # Merge events
                self.state_manager.merge_events(current, next_event)
                self.merged_count += 1
            else:
                merged.append(current)
                current = next_event
        
        merged.append(current)
        return merged
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get tracking statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "active_events": len(self.active_events),
            "discarded_events": self.discarded_count,
            "merged_events": self.merged_count,
        }
    
    def reset(self) -> None:
        """Reset tracker state."""
        self.active_events.clear()
        self.missing_frame_counts.clear()
        self.discarded_count = 0
        self.merged_count = 0
        self.logger.debug("Event tracker reset")
