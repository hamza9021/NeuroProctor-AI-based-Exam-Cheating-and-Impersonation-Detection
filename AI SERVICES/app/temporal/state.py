"""
Event state management.

This module provides state machine logic for tracking event lifecycles
through creation, activation, updates, and termination.
"""

from typing import Optional
from app.temporal.temporal_event import TemporalEvent, EventState
from app.utils.logger import get_logger


class EventStateManager:
    """
    Manages state transitions for temporal events.
    
    This class ensures events follow proper lifecycle transitions
    and provides logging for state changes.
    """
    
    def __init__(self):
        """Initialize event state manager."""
        self.logger = get_logger(__name__)
    
    def create_event(
        self,
        event_type: str,
        frame_number: int,
        timestamp: float,
        confidence: float,
        metadata: Optional[dict] = None,
    ) -> TemporalEvent:
        """
        Create a new temporal event.
        
        Args:
            event_type: Type of event
            frame_number: Frame number where event started
            timestamp: Timestamp where event started
            confidence: Initial confidence value
            metadata: Optional metadata dictionary
            
        Returns:
            New TemporalEvent instance
        """
        event = TemporalEvent(
            event_type=event_type,
            start_frame=frame_number,
            start_time=timestamp,
            average_confidence=confidence,
            state=EventState.CREATED,
            metadata=metadata or {},
        )
        event.add_confidence(confidence)
        
        self.logger.debug(
            f"Event created: {event_type} at frame {frame_number}, "
            f"confidence: {confidence:.2f}"
        )
        
        return event
    
    def activate_event(self, event: TemporalEvent) -> None:
        """
        Transition event to active state.
        
        Args:
            event: TemporalEvent to activate
        """
        if event.state == EventState.CREATED:
            event.update_state(EventState.ACTIVE)
            self.logger.debug(
                f"Event activated: {event.event_type} at frame {event.start_frame}"
            )
    
    def update_event(self, event: TemporalEvent, confidence: float) -> None:
        """
        Update an active event with new confidence.
        
        Args:
            event: TemporalEvent to update
            confidence: New confidence value
        """
        if event.is_active():
            event.add_confidence(confidence)
            event.update_state(EventState.UPDATED)
            self.logger.debug(
                f"Event updated: {event.event_type}, "
                f"confidence: {confidence:.2f}, "
                f"frame_count: {event.frame_count}"
            )
    
    def end_event(
        self,
        event: TemporalEvent,
        end_frame: int,
        end_time: float,
    ) -> None:
        """
        Transition event to ended state.
        
        Args:
            event: TemporalEvent to end
            end_frame: Frame number where event ended
            end_time: Timestamp where event ended
        """
        if event.is_active():
            event.end_event(end_frame, end_time)
            self.logger.info(
                f"Event ended: {event.event_type}, "
                f"duration: {event.duration:.2f}s, "
                f"frames: {event.frame_count}, "
                f"avg_confidence: {event.average_confidence:.2f}"
            )
    
    def discard_event(self, event: TemporalEvent, reason: str) -> None:
        """
        Discard an event (typically due to short duration).
        
        Args:
            event: TemporalEvent to discard
            reason: Reason for discarding
        """
        self.logger.debug(
            f"Event discarded: {event.event_type}, "
            f"reason: {reason}, "
            f"duration: {event.duration:.2f}s, "
            f"frames: {event.frame_count}"
        )
    
    def merge_events(self, primary: TemporalEvent, secondary: TemporalEvent) -> None:
        """
        Merge two events of the same type.
        
        Args:
            primary: Primary event to merge into
            secondary: Secondary event to merge from
        """
        # Merge confidence histories
        primary.confidence_history.extend(secondary.confidence_history)
        primary.frame_count += secondary.frame_count
        
        # Update end frame and time
        primary.end_frame = secondary.end_frame
        primary.end_time = secondary.end_time
        primary.duration = primary.end_time - primary.start_time
        
        # Recalculate average confidence
        primary._update_average_confidence()
        
        self.logger.info(
            f"Events merged: {primary.event_type}, "
            f"total_duration: {primary.duration:.2f}s, "
            f"total_frames: {primary.frame_count}"
        )
