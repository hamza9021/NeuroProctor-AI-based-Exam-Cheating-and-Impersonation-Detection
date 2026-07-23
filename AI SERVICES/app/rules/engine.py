"""
Rule Engine for event detection.

This module provides the main RuleEngine class that coordinates
rule evaluation and event generation.
"""

from typing import List, Optional
import time

from app.rules.context import RuleContext
from app.rules.evaluator import RuleEvaluator
from app.events.event import ExamEvent, FrameEvents
from app.rules.phone_rule import PhoneRule
from app.rules.multiple_person_rule import MultiplePersonRule
from app.rules.no_person_rule import NoPersonRule
from app.rules.looking_direction_rule import LookingDirectionRule
from app.rules.leaving_frame_rule import LeavingFrameRule
from app.utils.logger import get_logger


class RuleEngine:
    """Main rule engine for event detection."""

    def __init__(self):
        """Initialize rule engine with default rules."""
        self.logger = get_logger(__name__)
        self.evaluator = RuleEvaluator()
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default rules for exam monitoring."""
        self.evaluator.register_rule(PhoneRule())
        self.evaluator.register_rule(MultiplePersonRule())
        self.evaluator.register_rule(NoPersonRule())
        self.evaluator.register_rule(LookingDirectionRule())
        self.evaluator.register_rule(LeavingFrameRule())

        self.logger.info(f"Registered {self.evaluator.get_rule_count()} default rules")

    def register_rule(self, rule) -> None:
        """
        Register a custom rule.

        Args:
            rule: Rule instance to register
        """
        self.evaluator.register_rule(rule)
        self.logger.info(f"Registered custom rule: {rule.name}")

    def process(
        self,
        frame,
        frame_number: int,
        timestamp: float,
        detections: Optional = None,
        pose_result: Optional = None,
    ) -> FrameEvents:
        """
        Process a frame through the rule engine.

        Args:
            frame: Input frame as numpy array
            frame_number: Frame number
            timestamp: Frame timestamp
            detections: FrameDetections object
            pose_result: PoseResult object

        Returns:
            FrameEvents object containing all generated events
        """
        start_time = time.time()

        # Create context
        context = RuleContext(
            frame=frame,
            frame_number=frame_number,
            timestamp=timestamp,
            detections=detections,
            pose_result=pose_result,
        )

        # Evaluate all rules
        events = self.evaluator.evaluate_all(context)

        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Log summary
        if events:
            self.logger.debug(
                f"Frame {frame_number}: Generated {len(events)} events, "
                f"Processing: {processing_time:.2f}ms"
            )

        # Create frame events
        frame_events = FrameEvents(
            frame_number=frame_number,
            timestamp=timestamp,
            events=events,
        )

        return frame_events

    def get_rule_count(self) -> int:
        """
        Get number of registered rules.

        Returns:
            Number of rules
        """
        return self.evaluator.get_rule_count()
