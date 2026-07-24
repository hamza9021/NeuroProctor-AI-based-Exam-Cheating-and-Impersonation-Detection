"""
Sliding window implementation for temporal smoothing.

This module provides a sliding window data structure for efficient
event tracking and temporal analysis.
"""

from collections import deque
from typing import List, Optional, Any
from app.events.event import ExamEvent
from app.utils.logger import get_logger


class SlidingWindow:
    """
    Sliding window for tracking events over a fixed time window.
    
    This class maintains a fixed-size window of events for efficient
    temporal analysis and noise filtering.
    """
    
    def __init__(self, window_size: int):
        """
        Initialize sliding window.
        
        Args:
            window_size: Number of frames/events to keep in window
        """
        self.logger = get_logger(__name__)
        self.window_size = window_size
        self.window: deque = deque(maxlen=window_size)
        self.frame_numbers: deque = deque(maxlen=window_size)
    
    def add(self, event: ExamEvent, frame_number: int) -> None:
        """
        Add an event to the window.
        
        Args:
            event: Event to add
            frame_number: Frame number for this event
        """
        self.window.append(event)
        self.frame_numbers.append(frame_number)
    
    def add_frame_events(self, events: List[ExamEvent], frame_number: int) -> None:
        """
        Add multiple events for a single frame.
        
        Args:
            events: List of events for this frame
            frame_number: Frame number
        """
        for event in events:
            self.add(event, frame_number)
    
    def get_event_counts(self) -> dict:
        """
        Get count of each event type in the window.
        
        Returns:
            Dictionary mapping event types to counts
        """
        counts = {}
        for event in self.window:
            event_type = event.event_type.value
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
    
    def get_most_frequent_event(self) -> Optional[str]:
        """
        Get the most frequently occurring event type in the window.
        
        Returns:
            Most frequent event type or None if window is empty
        """
        if not self.window:
            return None
        
        counts = self.get_event_counts()
        if not counts:
            return None
        
        return max(counts.items(), key=lambda x: x[1])[0]
    
    def get_event_frequency(self, event_type: str) -> float:
        """
        Get frequency of a specific event type in the window.
        
        Args:
            event_type: Event type to check
            
        Returns:
            Frequency (0.0 to 1.0)
        """
        if not self.window:
            return 0.0
        
        counts = self.get_event_counts()
        return counts.get(event_type, 0) / len(self.window)
    
    def has_event(self, event_type: str, min_count: int = 1) -> bool:
        """
        Check if event type appears at least min_count times in window.
        
        Args:
            event_type: Event type to check
            min_count: Minimum count threshold
            
        Returns:
            True if event appears at least min_count times
        """
        counts = self.get_event_counts()
        return counts.get(event_type, 0) >= min_count
    
    def get_frame_range(self) -> tuple:
        """
        Get the range of frame numbers in the window.
        
        Returns:
            Tuple of (min_frame, max_frame) or (None, None) if empty
        """
        if not self.frame_numbers:
            return (None, None)
        return (min(self.frame_numbers), max(self.frame_numbers))
    
    def clear(self) -> None:
        """Clear the window."""
        self.window.clear()
        self.frame_numbers.clear()
        self.logger.debug("Sliding window cleared")
    
    def size(self) -> int:
        """
        Get current window size.
        
        Returns:
            Number of events in window
        """
        return len(self.window)
    
    def is_full(self) -> bool:
        """
        Check if window is full.
        
        Returns:
            True if window has reached max size
        """
        return len(self.window) == self.window_size
    
    def get_events_by_type(self, event_type: str) -> List[ExamEvent]:
        """
        Get all events of a specific type in the window.
        
        Args:
            event_type: Event type to filter by
            
        Returns:
            List of events of the specified type
        """
        return [e for e in self.window if e.event_type.value == event_type]
    
    def get_average_confidence(self, event_type: Optional[str] = None) -> float:
        """
        Get average confidence for events in the window.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            Average confidence or 0.0 if no events
        """
        if not self.window:
            return 0.0
        
        events = self.window
        if event_type:
            events = self.get_events_by_type(event_type)
        
        if not events:
            return 0.0
        
        return sum(e.confidence for e in events) / len(events)
