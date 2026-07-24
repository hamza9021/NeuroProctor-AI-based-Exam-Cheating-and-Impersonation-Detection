"""
Temporal smoother for event stabilization.

This module provides the main TemporalSmoother class that coordinates
event tracking, smoothing strategies, and temporal event generation.
"""

from typing import List, Optional
from app.temporal.tracker import EventTracker
from app.temporal.window import SlidingWindow
from app.temporal.strategies import SmoothingStrategy, SlidingWindowStrategy
from app.temporal.temporal_event import TemporalEvent, TemporalEventSequence
from app.events.event import ExamEvent, FrameEvents
from app.config.settings import settings
from app.utils.logger import get_logger


class TemporalSmoother:
    """
    Main temporal smoother for stabilizing rule engine events.
    
    This class receives frame-level events from the rule engine,
    applies smoothing strategies, and produces stable temporal events.
    """
    
    def __init__(
        self,
        strategy: Optional[SmoothingStrategy] = None,
        window_size: Optional[int] = None,
        min_duration: Optional[float] = None,
        merge_gap: Optional[float] = None,
        max_missing_frames: Optional[int] = None,
    ):
        """
        Initialize temporal smoother.
        
        Args:
            strategy: Smoothing strategy to use (default: SlidingWindowStrategy)
            window_size: Size of sliding window
            min_duration: Minimum event duration in seconds
            merge_gap: Maximum gap to merge consecutive events (seconds)
            max_missing_frames: Maximum frames event can be missing
        """
        self.logger = get_logger(__name__)
        
        # Use settings defaults if not provided
        self.window_size = window_size or getattr(settings, 'TEMPORAL_WINDOW_SIZE', 10)
        self.min_duration = min_duration or getattr(settings, 'TEMPORAL_MIN_DURATION', 0.5)
        self.merge_gap = merge_gap or getattr(settings, 'TEMPORAL_MERGE_GAP', 0.3)
        self.max_missing_frames = max_missing_frames or getattr(settings, 'TEMPORAL_MAX_MISSING_FRAMES', 5)
        
        # Initialize components
        self.strategy = strategy or SlidingWindowStrategy(
            window_size=self.window_size,
            min_count=getattr(settings, 'TEMPORAL_MIN_COUNT', 3),
        )
        self.tracker = EventTracker(max_missing_frames=self.max_missing_frames)
        self.window = SlidingWindow(window_size=self.window_size)
        
        # Event sequence
        self.event_sequence = TemporalEventSequence()
        
        # Current frame info
        self.current_frame_number = 0
        self.current_timestamp = 0.0
        
        self.logger.info(
            f"TemporalSmoother initialized with strategy: {self.strategy.name}, "
            f"window_size: {self.window_size}, "
            f"min_duration: {self.min_duration}s, "
            f"merge_gap: {self.merge_gap}s"
        )
    
    def process_frame(
        self,
        frame_events: FrameEvents,
        frame_number: int,
        timestamp: float,
    ) -> List[TemporalEvent]:
        """
        Process events for a single frame.
        
        Args:
            frame_events: FrameEvents from rule engine
            frame_number: Current frame number
            timestamp: Current timestamp
            
        Returns:
            List of newly ended temporal events
        """
        self.current_frame_number = frame_number
        self.current_timestamp = timestamp
        
        # Add events to sliding window
        self.window.add_frame_events(frame_events.events, frame_number)
        
        # Process events through tracker
        ended_events = self.tracker.process_frame_events(
            frame_events.events,
            frame_number,
            timestamp,
        )
        
        # Filter ended events by minimum duration
        valid_ended_events = []
        for event in ended_events:
            if not self.tracker.discard_short_event(event, self.min_duration):
                valid_ended_events.append(event)
                self.event_sequence.add_event(event)
        
        return valid_ended_events
    
    def finalize(self) -> List[TemporalEvent]:
        """
        Finalize processing and end all active events.
        
        Returns:
            List of ended events
        """
        # End all active events
        ended_events = self.tracker.end_all_events(
            self.current_frame_number,
            self.current_timestamp,
        )
        
        # Filter by minimum duration
        valid_ended_events = []
        for event in ended_events:
            if not self.tracker.discard_short_event(event, self.min_duration):
                valid_ended_events.append(event)
                self.event_sequence.add_event(event)
        
        # Merge consecutive events
        merged_events = self.tracker.merge_consecutive_events(
            valid_ended_events,
            self.merge_gap,
        )
        
        # Update event sequence with merged events
        self.event_sequence.events = merged_events
        
        self.logger.info(
            f"Temporal smoothing finalized. "
            f"Total events: {len(merged_events)}, "
            f"Discarded: {self.tracker.discarded_count}, "
            f"Merged: {self.tracker.merged_count}"
        )
        
        return merged_events
    
    def get_active_events(self) -> List[TemporalEvent]:
        """
        Get currently active temporal events.
        
        Returns:
            List of active events
        """
        return self.tracker.get_active_events()
    
    def get_event_sequence(self) -> TemporalEventSequence:
        """
        Get the complete event sequence.
        
        Returns:
            TemporalEventSequence containing all events
        """
        return self.event_sequence
    
    def get_statistics(self) -> dict:
        """
        Get smoothing statistics.
        
        Returns:
            Dictionary with statistics
        """
        tracker_stats = self.tracker.get_statistics()
        return {
            "window_size": self.window_size,
            "window_current_size": self.window.size(),
            "strategy": self.strategy.name,
            "min_duration": self.min_duration,
            "merge_gap": self.merge_gap,
            **tracker_stats,
        }
    
    def reset(self) -> None:
        """Reset smoother state."""
        self.tracker.reset()
        self.window.clear()
        self.event_sequence = TemporalEventSequence()
        self.current_frame_number = 0
        self.current_timestamp = 0.0
        self.logger.debug("TemporalSmoother reset")
    
    def set_strategy(self, strategy: SmoothingStrategy) -> None:
        """
        Change the smoothing strategy.
        
        Args:
            strategy: New smoothing strategy
        """
        self.strategy = strategy
        self.logger.info(f"Smoothing strategy changed to: {strategy.name}")
