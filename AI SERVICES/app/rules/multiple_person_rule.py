"""
Multiple person detection rule.

This rule detects when more than one person is present in the frame.
"""

from typing import List

from app.rules.evaluator import BaseRule
from app.rules.context import RuleContext
from app.events.event import ExamEvent
from app.events.event_types import EventType, EventSeverity
from app.config.settings import settings


class MultiplePersonRule(BaseRule):
    """Rule to detect multiple persons in frame."""

    def __init__(self):
        """Initialize multiple person rule."""
        super().__init__("MultiplePersonRule")

    def evaluate(self, context: RuleContext) -> List[ExamEvent]:
        """
        Evaluate if multiple persons are detected.

        Args:
            context: RuleContext containing detection data

        Returns:
            List of ExamEvent objects if multiple persons detected
        """
        events = []

        person_count = context.get_person_count()

        if person_count > settings.MAX_PERSONS:
            event = ExamEvent(
                event_type=EventType.MULTIPLE_PERSONS,
                severity=EventSeverity.CRITICAL,
                timestamp=context.timestamp,
                frame_number=context.frame_number,
                confidence=1.0,
                description=f"{person_count} persons detected (max allowed: {settings.MAX_PERSONS})",
                metadata={
                    "person_count": person_count,
                    "max_allowed": settings.MAX_PERSONS,
                },
            )
            events.append(event)

        return events
