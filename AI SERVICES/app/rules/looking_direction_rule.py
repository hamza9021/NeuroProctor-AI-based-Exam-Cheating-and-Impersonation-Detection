"""
Looking direction rule.

This rule detects head orientation using pose keypoints.
"""

from typing import List, Optional
import math

from app.rules.evaluator import BaseRule
from app.rules.context import RuleContext
from app.events.event import ExamEvent
from app.events.event_types import EventType, EventSeverity
from app.config.settings import settings


class LookingDirectionRule(BaseRule):
    """Rule to detect head orientation."""

    def __init__(self):
        """Initialize looking direction rule."""
        super().__init__("LookingDirectionRule")

    def evaluate(self, context: RuleContext) -> List[ExamEvent]:
        """
        Evaluate head orientation using pose keypoints.

        Args:
            context: RuleContext containing pose data

        Returns:
            List of ExamEvent objects for head direction
        """
        events = []

        if not context.has_poses():
            return events

        for person in context.pose_result.persons:
            head_direction = self._calculate_head_direction(person.keypoints)

            if head_direction == "left":
                event = ExamEvent(
                    event_type=EventType.LOOKING_LEFT,
                    severity=EventSeverity.WARNING,
                    timestamp=context.timestamp,
                    frame_number=context.frame_number,
                    confidence=0.8,
                    description="Person looking left",
                    metadata={
                        "person_id": person.person_id,
                        "direction": "left",
                    },
                )
                events.append(event)
            elif head_direction == "right":
                event = ExamEvent(
                    event_type=EventType.LOOKING_RIGHT,
                    severity=EventSeverity.WARNING,
                    timestamp=context.timestamp,
                    frame_number=context.frame_number,
                    confidence=0.8,
                    description="Person looking right",
                    metadata={
                        "person_id": person.person_id,
                        "direction": "right",
                    },
                )
                events.append(event)
            elif head_direction == "down":
                event = ExamEvent(
                    event_type=EventType.LOOKING_DOWN,
                    severity=EventSeverity.WARNING,
                    timestamp=context.timestamp,
                    frame_number=context.frame_number,
                    confidence=0.8,
                    description="Person looking down",
                    metadata={
                        "person_id": person.person_id,
                        "direction": "down",
                    },
                )
                events.append(event)

        return events

    def _calculate_head_direction(self, keypoints) -> Optional[str]:
        """
        Calculate head direction from keypoints.

        Args:
            keypoints: Keypoints object

        Returns:
            Direction string or None if cannot determine
        """
        # Get eye and nose keypoints
        left_eye = keypoints.get_keypoint_by_name("left_eye")
        right_eye = keypoints.get_keypoint_by_name("right_eye")
        nose = keypoints.get_keypoint_by_name("nose")

        if not all([left_eye, right_eye, nose]):
            return None

        # Calculate horizontal eye center
        eye_center_x = (left_eye.x + right_eye.x) / 2

        # Calculate horizontal offset of nose from eye center
        nose_offset = nose.x - eye_center_x

        # Calculate eye distance for normalization
        eye_distance = abs(right_eye.x - left_eye.x)

        if eye_distance == 0:
            return None

        # Normalize offset
        normalized_offset = nose_offset / eye_distance

        # Calculate angle in degrees
        angle = math.degrees(math.atan(normalized_offset))

        # Determine direction based on angle threshold
        if abs(angle) > settings.HEAD_TURN_THRESHOLD:
            if angle > 0:
                return "right"
            else:
                return "left"

        # Check for looking down using nose vs eye vertical position
        eye_center_y = (left_eye.y + right_eye.y) / 2
        nose_vertical_offset = nose.y - eye_center_y

        if nose_vertical_offset > eye_distance * 0.5:
            return "down"

        return None
