"""
Phone detection rule.

This rule detects when a cell phone is present in the frame.
"""

from typing import List

from app.rules.evaluator import BaseRule
from app.rules.context import RuleContext
from app.events.event import ExamEvent
from app.events.event_types import EventType, EventSeverity
from app.config.settings import settings


class PhoneRule(BaseRule):
    """Rule to detect cell phone presence."""

    def __init__(self):
        """Initialize phone rule."""
        super().__init__("PhoneRule")

    def evaluate(self, context: RuleContext) -> List[ExamEvent]:
        """
        Evaluate if a cell phone is detected.

        Args:
            context: RuleContext containing detection data

        Returns:
            List of ExamEvent objects if phone detected
        """
        events = []

        if not context.has_detections():
            return events

        phone_detections = context.get_detections_by_class("cell phone")

        for detection in phone_detections:
            if detection.confidence >= settings.PHONE_CONFIDENCE_THRESHOLD:
                event = ExamEvent(
                    event_type=EventType.PHONE_DETECTED,
                    severity=EventSeverity.CRITICAL,
                    timestamp=context.timestamp,
                    frame_number=context.frame_number,
                    confidence=detection.confidence,
                    description=f"Cell phone detected with {detection.confidence:.0%} confidence",
                    metadata={
                        "bounding_box": detection.bounding_box,
                        "center_point": detection.center_point,
                    },
                )
                events.append(event)

        return events
