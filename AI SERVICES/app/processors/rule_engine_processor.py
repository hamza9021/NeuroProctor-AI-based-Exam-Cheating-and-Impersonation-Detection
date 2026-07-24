"""
Rule Engine Processor module.

This module provides a processor that integrates the Rule Engine
with the video processing pipeline.
"""

import numpy as np
import cv2
from typing import Optional, List

from app.processors.base_processor import BaseProcessor
from app.rules.engine import RuleEngine
from app.events.event import FrameEvents
from app.events.event_types import EventSeverity
from app.config.settings import settings
from app.utils.logger import get_logger


class RuleEngineProcessor(BaseProcessor):
    """Processor for rule engine event detection in video frames."""

    def __init__(self):
        """Initialize rule engine processor."""
        super().__init__("RuleEngineProcessor")
        
        self.logger = get_logger(__name__)
        self.rule_engine = RuleEngine()
        
        self.current_frame_number: int = 0
        self.current_timestamp: float = 0.0
        self.last_frame_events: Optional[FrameEvents] = None
        self.all_frame_events: List[FrameEvents] = []
        
        # References to previous processor outputs
        self.last_detections = None
        self.last_pose_result = None
        self.last_frame_tracks = None
        self.last_head_poses = None

    def initialize(self) -> None:
        """Initialize the rule engine."""
        try:
            self.logger.info(f"RuleEngineProcessor initialized with {self.rule_engine.get_rule_count()} rules")
        except Exception as e:
            self.logger.error(f"Failed to initialize RuleEngineProcessor: {e}")
            raise

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame with rule engine.

        Args:
            frame: Input frame as numpy array

        Returns:
            Annotated frame with events drawn
        """
        # Process through rule engine
        frame_events = self.rule_engine.process(
            frame=frame,
            frame_number=self.current_frame_number,
            timestamp=self.current_timestamp,
            detections=self.last_detections,
            pose_result=self.last_pose_result,
            head_poses=self.last_head_poses,
        )

        # Associate events with Track IDs if tracking data is available
        if self.last_frame_tracks:
            frame_events = self._associate_events_with_tracks(frame_events)

        # Store frame events
        self.last_frame_events = frame_events
        self.all_frame_events.append(frame_events)

        # Draw events on frame
        annotated_frame = self._draw_events(frame, frame_events)

        # Log event summary periodically
        if self.current_frame_number % 100 == 0:
            event_count = frame_events.get_event_count()
            tracked_event_count = sum(1 for e in frame_events.events if e.track_id is not None)
            if event_count > 0:
                self.logger.info(
                    f"Frame {self.current_frame_number}: "
                    f"Events: {event_count}, "
                    f"Tracked: {tracked_event_count}, "
                    f"Critical: {len(frame_events.get_events_by_severity('CRITICAL'))}"
                )

        return annotated_frame

    def _draw_events(self, frame: np.ndarray, frame_events: FrameEvents) -> np.ndarray:
        """
        Draw events on frame.

        Args:
            frame: Input frame
            frame_events: FrameEvents object

        Returns:
            Frame with events drawn
        """
        annotated_frame = frame.copy()

        if frame_events.get_event_count() == 0:
            return annotated_frame

        # Draw event panel
        self._draw_event_panel(annotated_frame, frame_events)

        return annotated_frame

    def _draw_event_panel(self, frame: np.ndarray, frame_events: FrameEvents) -> None:
        """
        Draw event panel on frame.

        Args:
            frame: Frame to draw on
            frame_events: FrameEvents object
        """
        # Panel settings - smaller size
        panel_height = 250
        panel_width = 320
        margin = 10
        
        # Get unique event types to avoid duplicates
        seen_types = set()
        unique_events = []
        for event in frame_events.events:
            if event.event_type.value not in seen_types:
                seen_types.add(event.event_type.value)
                unique_events.append(event)
        
        # Draw semi-transparent panel background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (margin, margin),
            (margin + panel_width, margin + panel_height),
            (0, 0, 0),
            -1,
        )
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Draw panel border
        cv2.rectangle(
            frame,
            (margin, margin),
            (margin + panel_width, margin + panel_height),
            (255, 255, 255),
            2,
        )
        
        # Draw header
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        text_color = (255, 255, 255)
        
        header_text = f"EVENTS: {len(unique_events)}"
        cv2.putText(
            frame,
            header_text,
            (margin + 10, margin + 25),
            font,
            font_scale,
            text_color,
            font_thickness,
        )
        
        # Draw separator line
        cv2.line(
            frame,
            (margin + 10, margin + 35),
            (margin + panel_width - 10, margin + 35),
            (255, 255, 255),
            1,
        )
        
        # Draw events
        y_offset = margin + 55
        for event in unique_events[:6]:  # Limit to 6 events
            # Color based on severity
            if event.severity.value == "CRITICAL":
                color = (0, 0, 255)  # Red
                symbol = "[!]"
            elif event.severity.value == "WARNING":
                color = (0, 165, 255)  # Orange
                symbol = "[!]"
            else:
                color = (0, 255, 0)  # Green
                symbol = "[i]"
            
            # Draw event text
            event_text = f"{symbol} {event.event_type.value}"
            cv2.putText(
                frame,
                event_text,
                (margin + 10, y_offset),
                font,
                0.5,
                color,
                2,
            )
            
            # Draw confidence if available
            if event.confidence > 0:
                conf_text = f"Conf: {event.confidence:.0%}"
                cv2.putText(
                    frame,
                    conf_text,
                    (margin + 10, y_offset + 18),
                    font,
                    0.4,
                    (200, 200, 200),
                    1,
                )
                y_offset += 35
            else:
                y_offset += 20

    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("RuleEngineProcessor cleaned up")

    def set_frame_context(self, frame_number: int, timestamp: float) -> None:
        """
        Set frame context for processing.

        Args:
            frame_number: Current frame number
            timestamp: Current frame timestamp
        """
        self.current_frame_number = frame_number
        self.current_timestamp = timestamp

    def set_detections(self, detections) -> None:
        """
        Set detections from object detection processor.

        Args:
            detections: FrameDetections object
        """
        self.last_detections = detections

    def set_pose_result(self, pose_result) -> None:
        """
        Set pose result from pose processor.

        Args:
            pose_result: PoseResult object
        """
        self.last_pose_result = pose_result
    
    def set_frame_tracks(self, frame_tracks) -> None:
        """
        Set frame tracks from tracking processor.

        Args:
            frame_tracks: FrameTracks object with track information
        """
        self.last_frame_tracks = frame_tracks
    
    def set_head_poses(self, head_poses) -> None:
        """
        Set head poses from head pose processor.

        Args:
            head_poses: FrameHeadPoses object with head pose estimates
        """
        self.last_head_poses = head_poses
    
    def _associate_events_with_tracks(self, frame_events) -> FrameEvents:
        """
        Associate events with Track IDs using pose track information.
        
        Args:
            frame_events: FrameEvents object with events
            
        Returns:
            FrameEvents with track IDs assigned to events
        """
        if not self.last_pose_result or not self.last_frame_tracks:
            return frame_events
        
        # Create mapping from track_id to track
        track_map = {t.track_id: t for t in self.last_frame_tracks.tracks if t.is_active()}
        
        for event in frame_events.events:
            # Check if event has pose information in metadata
            if event.metadata and 'person_id' in event.metadata:
                person_id = event.metadata['person_id']
                
                # Find the corresponding person pose
                try:
                    person_pose = self.last_pose_result.get_person_by_id(person_id)
                    if person_pose.track_id is not None:
                        event.track_id = person_pose.track_id
                except ValueError:
                    # Person not found, skip
                    pass
        
        return frame_events

    def get_last_frame_events(self) -> Optional[FrameEvents]:
        """
        Get events from the last processed frame.

        Returns:
            FrameEvents object or None if no frame processed yet
        """
        return self.last_frame_events

    def get_all_frame_events(self) -> List[FrameEvents]:
        """
        Get all events from processed frames.

        Returns:
            List of FrameEvents objects
        """
        return self.all_frame_events

    def clear_events_history(self) -> None:
        """Clear the history of all frame events."""
        self.all_frame_events.clear()
        self.last_frame_events = None
