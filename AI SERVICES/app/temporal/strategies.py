"""
Smoothing strategies for temporal event processing.

This module provides the Strategy Pattern implementation for different
smoothing algorithms that can be plugged into the temporal smoother.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.events.event import ExamEvent
from app.temporal.window import SlidingWindow
from app.utils.logger import get_logger


class SmoothingStrategy(ABC):
    """Abstract base class for smoothing strategies."""
    
    def __init__(self, name: str):
        """
        Initialize smoothing strategy.
        
        Args:
            name: Name of the strategy
        """
        self.name = name
        self.logger = get_logger(__name__)
    
    @abstractmethod
    def should_emit_event(
        self,
        event_type: str,
        window: SlidingWindow,
        current_frame: int,
    ) -> bool:
        """
        Determine if an event should be emitted based on strategy.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            current_frame: Current frame number
            
        Returns:
            True if event should be emitted
        """
        pass
    
    @abstractmethod
    def get_confidence(
        self,
        event_type: str,
        window: SlidingWindow,
    ) -> float:
        """
        Get confidence value for event type based on strategy.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            
        Returns:
            Confidence value
        """
        pass


class SlidingWindowStrategy(SmoothingStrategy):
    """
    Sliding window smoothing strategy.
    
    Emits event if it appears at least min_count times in the window.
    """
    
    def __init__(self, window_size: int = 10, min_count: int = 3):
        """
        Initialize sliding window strategy.
        
        Args:
            window_size: Size of sliding window
            min_count: Minimum count to emit event
        """
        super().__init__("SlidingWindow")
        self.window_size = window_size
        self.min_count = min_count
    
    def should_emit_event(
        self,
        event_type: str,
        window: SlidingWindow,
        current_frame: int,
    ) -> bool:
        """
        Check if event appears at least min_count times in window.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            current_frame: Current frame number
            
        Returns:
            True if event appears at least min_count times
        """
        return window.has_event(event_type, self.min_count)
    
    def get_confidence(
        self,
        event_type: str,
        window: SlidingWindow,
    ) -> float:
        """
        Get average confidence for event type.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            
        Returns:
            Average confidence
        """
        return window.get_average_confidence(event_type)


class MajorityVotingStrategy(SmoothingStrategy):
    """
    Majority voting smoothing strategy.
    
    Emits event if it's the most frequent event in the window.
    """
    
    def __init__(self, window_size: int = 15, min_frequency: float = 0.5):
        """
        Initialize majority voting strategy.
        
        Args:
            window_size: Size of sliding window
            min_frequency: Minimum frequency (0.0 to 1.0) to emit event
        """
        super().__init__("MajorityVoting")
        self.window_size = window_size
        self.min_frequency = min_frequency
    
    def should_emit_event(
        self,
        event_type: str,
        window: SlidingWindow,
        current_frame: int,
    ) -> bool:
        """
        Check if event is the majority in the window.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            current_frame: Current frame number
            
        Returns:
            True if event is majority
        """
        frequency = window.get_event_frequency(event_type)
        return frequency >= self.min_frequency
    
    def get_confidence(
        self,
        event_type: str,
        window: SlidingWindow,
    ) -> float:
        """
        Get frequency as confidence.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            
        Returns:
            Frequency as confidence
        """
        return window.get_event_frequency(event_type)


class MinimumDurationStrategy(SmoothingStrategy):
    """
    Minimum duration smoothing strategy.
    
    Emits event only if it has been present for minimum duration.
    This is typically used in conjunction with event tracking.
    """
    
    def __init__(self, min_duration_frames: int = 5):
        """
        Initialize minimum duration strategy.
        
        Args:
            min_duration_frames: Minimum frames to emit event
        """
        super().__init__("MinimumDuration")
        self.min_duration_frames = min_duration_frames
    
    def should_emit_event(
        self,
        event_type: str,
        window: SlidingWindow,
        current_frame: int,
    ) -> bool:
        """
        Check if event has been present for minimum duration.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            current_frame: Current frame number
            
        Returns:
            True if event has been present for minimum duration
        """
        if not window.has_event(event_type, min_count=1):
            return False
        
        # Check if event has been present for minimum frames
        events = window.get_events_by_type(event_type)
        if not events:
            return False
        
        # Get frame range of this event type
        frame_range = window.get_frame_range()
        if frame_range[0] is None:
            return False
        
        duration_frames = frame_range[1] - frame_range[0] + 1
        return duration_frames >= self.min_duration_frames
    
    def get_confidence(
        self,
        event_type: str,
        window: SlidingWindow,
    ) -> float:
        """
        Get average confidence for event type.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            
        Returns:
            Average confidence
        """
        return window.get_average_confidence(event_type)


class HybridStrategy(SmoothingStrategy):
    """
    Hybrid smoothing strategy combining multiple strategies.
    
    Emits event if all sub-strategies agree.
    """
    
    def __init__(self, strategies: List[SmoothingStrategy]):
        """
        Initialize hybrid strategy.
        
        Args:
            strategies: List of strategies to combine
        """
        super().__init__("Hybrid")
        self.strategies = strategies
    
    def should_emit_event(
        self,
        event_type: str,
        window: SlidingWindow,
        current_frame: int,
    ) -> bool:
        """
        Check if all sub-strategies agree to emit event.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            current_frame: Current frame number
            
        Returns:
            True if all strategies agree
        """
        return all(
            strategy.should_emit_event(event_type, window, current_frame)
            for strategy in self.strategies
        )
    
    def get_confidence(
        self,
        event_type: str,
        window: SlidingWindow,
    ) -> float:
        """
        Get average confidence from all strategies.
        
        Args:
            event_type: Event type to check
            window: Sliding window of recent events
            
        Returns:
            Average confidence from all strategies
        """
        confidences = [
            strategy.get_confidence(event_type, window)
            for strategy in self.strategies
        ]
        return sum(confidences) / len(confidences) if confidences else 0.0
