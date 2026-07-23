"""
Leaving frame detection rule.

This rule detects when a person is partially or completely outside the frame.
"""

from typing import List

from app.rules.evaluator import BaseRule
from app.rules.context import RuleContext
from app.events.event import ExamEvent
from app.events.event_types import EventType, EventSeverity
from app.config.settings import settings


class LeavingFrameRule(BaseRule):
    """Rule to detect person leaving frame."""

    def __init__(self):
        """Initialize leaving frame rule."""
        super().__init__("LeavingFrameRule")

    def evaluate(self, context: RuleContext) -> List[ExamEvent]:
        """
        Evaluate if person is leaving the frame.

        Args:
            context: RuleContext containing pose data

        Returns:
            List of ExamEvent objects if person is leaving frame
        """
        events = []

        if not context.has_poses():
            return events

        margin = settings.FRAME_BOUNDARY_MARGIN
        margin_x = context.frame_width * margin
        margin_y = context.frame_height * margin

        for person in context.pose_result.persons:
            x1, y1, x2, y2 = person.bounding_box

            # Check if bounding box is near or outside frame boundaries
            is_near_left = x1 < margin_x
            is_near_right = x2 > context.frame_width - margin_x
            is_near_top = y1 < margin_y
            is_near_bottom = y2 > context.frame_height - margin_y

            if is_near_left or is_near_right or is_near_top or is_near_bottom:
                event = ExamEvent(
                    event_type=EventType.PERSON_LEFT_FRAME,
                    severity=EventSeverity.WARNING,
                    timestamp=context.timestamp,
                    frame_number=context.frame_number,
                    confidence=person.confidence,
                    description="Person near or outside frame boundaries",
                    metadata={
                        "person_id": person.person_id,
                        "bounding_box": person.bounding_box,
                        "near_left": is_near_left,
                        "near_right": is_near_right,
                        "near_top": is_near_top,
                        "near_bottom": is_near_bottom,
                    },
                )
                events.append(event)

        return events
