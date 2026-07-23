"""
No person detection rule.

This rule detects when no person is visible in the frame.
"""

from typing import List

from app.rules.evaluator import BaseRule
from app.rules.context import RuleContext
from app.events.event import ExamEvent
from app.events.event_types import EventType, EventSeverity


class NoPersonRule(BaseRule):
    """Rule to detect when no person is visible."""

    def __init__(self):
        """Initialize no person rule."""
        super().__init__("NoPersonRule")

    def evaluate(self, context: RuleContext) -> List[ExamEvent]:
        """
        Evaluate if no person is detected.

        Args:
            context: RuleContext containing detection data

        Returns:
            List of ExamEvent objects if no person detected
        """
        events = []

        person_count = context.get_person_count()

        if person_count == 0:
            event = ExamEvent(
                event_type=EventType.NO_PERSON_VISIBLE,
                severity=EventSeverity.WARNING,
                timestamp=context.timestamp,
                frame_number=context.frame_number,
                confidence=1.0,
                description="No person visible in frame",
                metadata={
                    "person_count": 0,
                },
            )
            events.append(event)

        return events
