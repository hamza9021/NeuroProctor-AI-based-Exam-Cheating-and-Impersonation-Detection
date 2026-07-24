"""
Temporal Processor module.

This module provides a processor that integrates the Temporal Smoother
with the video processing pipeline.
"""

import numpy as np
import cv2
from typing import Optional, List

from app.processors.base_processor import BaseProcessor
from app.temporal.smoother import TemporalSmoother
from app.temporal.temporal_event import TemporalEvent
from app.events.event import FrameEvents
from app.config.settings import settings
from app.utils.logger import get_logger


class TemporalProcessor(BaseProcessor):
    """Processor for temporal smoothing of rule engine events."""

    def __init__(self):
        """Initialize temporal processor."""
        super().__init__("TemporalProcessor")
        
        self.logger = get_logger(__name__)
        self.temporal_smoother = TemporalSmoother()
        
        self.current_frame_number: int = 0
        self.current_timestamp: float = 0.0
        self.last_frame_events: Optional[FrameEvents] = None
        
        # References to rule engine processor output
        self.last_rule_engine_events: Optional[FrameEvents] = None
        self.last_frame_tracks = None

    def initialize(self) -> None:
        """Initialize the temporal smoother."""
        try:
            self.logger.info("TemporalProcessor initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize TemporalProcessor: {e}")
            raise

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame with temporal smoothing.

        Args:
            frame: Input frame as numpy array

        Returns:
            Annotated frame with temporal events drawn
        """
        # Process through temporal smoother if we have rule engine events
        if self.last_rule_engine_events:
            # Group events by track_id for per-track temporal smoothing
            if self.last_frame_tracks:
                ended_events = self._process_per_track_temporal_smoothing()
            else:
                # Fallback to global smoothing if no tracking data
                ended_events = self.temporal_smoother.process_frame(
                    frame_events=self.last_rule_engine_events,
                    frame_number=self.current_frame_number,
                    timestamp=self.current_timestamp,
                )
            
            # Log ended events
            for event in ended_events:
                track_info = f" (Track {event.track_id})" if event.track_id else ""
                self.logger.info(
                    f"Temporal event ended: {event.event_type}{track_info}, "
                    f"duration: {event.duration:.2f}s, "
                    f"frames: {event.frame_count}"
                )
        
        # Draw active temporal events on frame
        annotated_frame = self._draw_temporal_events(frame)
        
        # Log active events periodically
        if self.current_frame_number % 100 == 0:
            active_events = self.temporal_smoother.get_active_events()
            if active_events:
                tracked_count = sum(1 for e in active_events if e.track_id is not None)
                self.logger.info(
                    f"Frame {self.current_frame_number}: "
                    f"Active temporal events: {len(active_events)}, "
                    f"Tracked: {tracked_count}"
                )

        return annotated_frame

    def _draw_temporal_events(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw active temporal events on frame.

        Args:
            frame: Input frame

        Returns:
            Frame with temporal events drawn
        """
        annotated_frame = frame.copy()
        
        active_events = self.temporal_smoother.get_active_events()
        
        if not active_events:
            return annotated_frame
        
        # Draw temporal event panel
        self._draw_temporal_panel(annotated_frame, active_events)
        
        return annotated_frame

    def _draw_temporal_panel(self, frame: np.ndarray, active_events: List[TemporalEvent]) -> None:
        """
        Draw temporal event panel on frame.

        Args:
            frame: Frame to draw on
            active_events: List of active temporal events
        """
        # Panel settings
        panel_height = 200
        panel_width = 320
        margin = 10
        start_x = 340  # Start after rule engine panel
        
        # Check if panel would fit, adjust if needed
        if start_x + panel_width > frame.shape[1]:
            start_x = frame.shape[1] - panel_width - margin
        
        # Draw semi-transparent panel background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (start_x, margin),
            (start_x + panel_width, margin + panel_height),
            (0, 0, 0),
            -1,
        )
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Draw panel border
        cv2.rectangle(
            frame,
            (start_x, margin),
            (start_x + panel_width, margin + panel_height),
            (0, 255, 255),  # Cyan border for temporal events
            2,
        )
        
        # Draw header
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        text_color = (0, 255, 255)
        
        header_text = f"TEMPORAL EVENTS: {len(active_events)}"
        cv2.putText(
            frame,
            header_text,
            (start_x + 10, margin + 25),
            font,
            font_scale,
            text_color,
            font_thickness,
        )
        
        # Draw separator line
        cv2.line(
            frame,
            (start_x + 10, margin + 35),
            (start_x + panel_width - 10, margin + 35),
            (0, 255, 255),
            1,
        )
        
        # Draw active events
        y_offset = margin + 55
        for event in active_events[:5]:  # Limit to 5 events
            # Calculate current duration
            current_duration = self.current_timestamp - event.start_time
            
            # Draw event text
            event_text = f"• {event.event_type}"
            cv2.putText(
                frame,
                event_text,
                (start_x + 10, y_offset),
                font,
                0.5,
                (255, 255, 255),
                2,
            )
            
            # Draw duration
            duration_text = f"Duration: {current_duration:.1f}s"
            cv2.putText(
                frame,
                duration_text,
                (start_x + 10, y_offset + 18),
                font,
                0.4,
                (200, 200, 200),
                1,
            )
            
            # Draw confidence
            conf_text = f"Conf: {event.average_confidence:.0%}"
            cv2.putText(
                frame,
                conf_text,
                (start_x + 10, y_offset + 34),
                font,
                0.4,
                (200, 200, 200),
                1,
            )
            
            y_offset += 50

    def cleanup(self) -> None:
        """Clean up resources."""
        # Finalize temporal smoothing
        final_events = self.temporal_smoother.finalize()
        
        # Log final statistics
        stats = self.temporal_smoother.get_statistics()
        self.logger.info(
            f"TemporalProcessor cleanup - "
            f"Total events: {len(final_events)}, "
            f"Discarded: {stats['discarded_events']}, "
            f"Merged: {stats['merged_events']}"
        )
        
        self.logger.info("TemporalProcessor cleaned up")

    def set_frame_context(self, frame_number: int, timestamp: float) -> None:
        """
        Set frame context for processing.

        Args:
            frame_number: Current frame number
            timestamp: Current frame timestamp
        """
        self.current_frame_number = frame_number
        self.current_timestamp = timestamp

    def set_rule_engine_events(self, frame_events: FrameEvents) -> None:
        """
        Set events from rule engine processor.

        Args:
            frame_events: FrameEvents object
        """
        self.last_rule_engine_events = frame_events
    
    def set_frame_tracks(self, frame_tracks) -> None:
        """
        Set frame tracks from tracking processor.

        Args:
            frame_tracks: FrameTracks object with track information
        """
        self.last_frame_tracks = frame_tracks
    
    def _process_per_track_temporal_smoothing(self) -> List:
        """
        Process temporal smoothing per track for better event tracking.
        
        Returns:
            List of ended temporal events
        """
        from collections import defaultdict
        
        # Group events by track_id
        events_by_track = defaultdict(list)
        untracked_events = []
        
        for event in self.last_rule_engine_events.events:
            if event.track_id is not None:
                events_by_track[event.track_id].append(event)
            else:
                untracked_events.append(event)
        
        all_ended_events = []
        
        # Process each track's events separately
        for track_id, track_events in events_by_track.items():
            # Create a FrameEvents object for this track
            track_frame_events = FrameEvents(
                frame_number=self.current_frame_number,
                timestamp=self.current_timestamp,
                events=track_events
            )
            
            # Process through temporal smoother
            ended_events = self.temporal_smoother.process_frame(
                frame_events=track_frame_events,
                frame_number=self.current_frame_number,
                timestamp=self.current_timestamp,
            )
            
            all_ended_events.extend(ended_events)
        
        # Process untracked events globally
        if untracked_events:
            untracked_frame_events = FrameEvents(
                frame_number=self.current_frame_number,
                timestamp=self.current_timestamp,
                events=untracked_events
            )
            
            ended_events = self.temporal_smoother.process_frame(
                frame_events=untracked_frame_events,
                frame_number=self.current_frame_number,
                timestamp=self.current_timestamp,
            )
            
            all_ended_events.extend(ended_events)
        
        return all_ended_events

    def get_temporal_smoother(self) -> TemporalSmoother:
        """
        Get the temporal smoother instance.

        Returns:
            TemporalSmoother instance
        """
        return self.temporal_smoother

    def get_event_sequence(self):
        """
        Get the complete temporal event sequence.

        Returns:
            TemporalEventSequence containing all events
        """
        return self.temporal_smoother.get_event_sequence()
