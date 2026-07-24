"""
Temporal event data models.

This module provides data structures for smoothed temporal events
that represent stable event sequences over time.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class EventState(Enum):
    """Event lifecycle states."""
    CREATED = "created"
    ACTIVE = "active"
    UPDATED = "updated"
    ENDED = "ended"


@dataclass
class TemporalEvent:
    """
    Represents a stable temporal event over a time range.
    
    This is the output of temporal smoothing, representing
    merged and filtered events with duration information.
    """
    
    event_type: str
    start_frame: int
    end_frame: Optional[int] = None
    start_time: float = 0.0
    end_time: Optional[float] = None
    duration: float = 0.0
    average_confidence: float = 0.0
    confidence_history: list = field(default_factory=list)
    frame_count: int = 0
    state: EventState = EventState.CREATED
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate duration if end time is available."""
        if self.end_time is not None:
            self.duration = self.end_time - self.start_time
    
    def add_confidence(self, confidence: float) -> None:
        """
        Add a confidence value to the history.
        
        Args:
            confidence: Confidence value to add
        """
        self.confidence_history.append(confidence)
        self.frame_count += 1
        self._update_average_confidence()
    
    def _update_average_confidence(self) -> None:
        """Update the average confidence from history."""
        if self.confidence_history:
            self.average_confidence = sum(self.confidence_history) / len(self.confidence_history)
    
    def end_event(self, end_frame: int, end_time: float) -> None:
        """
        Mark the event as ended.
        
        Args:
            end_frame: Frame number where event ended
            end_time: Timestamp where event ended
        """
        self.end_frame = end_frame
        self.end_time = end_time
        self.duration = end_time - self.start_time
        self.state = EventState.ENDED
    
    def update_state(self, new_state: EventState) -> None:
        """
        Update the event state.
        
        Args:
            new_state: New state to set
        """
        self.state = new_state
    
    def is_active(self) -> bool:
        """
        Check if event is currently active.
        
        Returns:
            True if event is active
        """
        return self.state in [EventState.CREATED, EventState.ACTIVE, EventState.UPDATED]
    
    def is_ended(self) -> bool:
        """
        Check if event has ended.
        
        Returns:
            True if event has ended
        """
        return self.state == EventState.ENDED
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "event": self.event_type,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "start_time": round(self.start_time, 2),
            "end_time": round(self.end_time, 2) if self.end_time else None,
            "duration": round(self.duration, 2),
            "average_confidence": round(self.average_confidence, 2),
            "frame_count": self.frame_count,
            "state": self.state.value,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemporalEvent":
        """
        Create TemporalEvent from dictionary.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            TemporalEvent instance
        """
        return cls(
            event_type=data["event"],
            start_frame=data["start_frame"],
            end_frame=data.get("end_frame"),
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            duration=data["duration"],
            average_confidence=data["average_confidence"],
            confidence_history=data.get("confidence_history", []),
            frame_count=data.get("frame_count", 0),
            state=EventState(data.get("state", "created")),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TemporalEventSequence:
    """
    Container for all temporal events from a video.
    """
    
    events: list[TemporalEvent] = field(default_factory=list)
    
    def add_event(self, event: TemporalEvent) -> None:
        """
        Add a temporal event to the sequence.
        
        Args:
            event: TemporalEvent to add
        """
        self.events.append(event)
    
    def get_active_events(self) -> list[TemporalEvent]:
        """
        Get all currently active events.
        
        Returns:
            List of active events
        """
        return [e for e in self.events if e.is_active()]
    
    def get_ended_events(self) -> list[TemporalEvent]:
        """
        Get all ended events.
        
        Returns:
            List of ended events
        """
        return [e for e in self.events if e.is_ended()]
    
    def get_events_by_type(self, event_type: str) -> list[TemporalEvent]:
        """
        Get events of a specific type.
        
        Returns:
            List of events of the specified type
        """
        return [e for e in self.events if e.event_type == event_type]
    
    def get_event_count(self) -> int:
        """
        Get total number of events.
        
        Returns:
            Number of events
        """
        return len(self.events)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the sequence
        """
        return {
            "total_events": len(self.events),
            "active_events": len(self.get_active_events()),
            "ended_events": len(self.get_ended_events()),
            "events": [e.to_dict() for e in self.events],
        }
