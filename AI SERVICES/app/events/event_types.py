"""
Event types for exam monitoring.

This module defines the enum for all possible event types
that can be detected during exam monitoring.
"""

from enum import Enum


class EventType(Enum):
    """Enum for all event types in exam monitoring."""

    # Person-related events
    PERSON_DETECTED = "PERSON_DETECTED"
    NO_PERSON_VISIBLE = "NO_PERSON_VISIBLE"
    MULTIPLE_PERSONS = "MULTIPLE_PERSONS"
    PERSON_LEFT_FRAME = "PERSON_LEFT_FRAME"

    # Object-related events
    PHONE_DETECTED = "PHONE_DETECTED"
    LAPTOP_DETECTED = "LAPTOP_DETECTED"
    BOOK_DETECTED = "BOOK_DETECTED"
    KEYBOARD_DETECTED = "KEYBOARD_DETECTED"
    MOUSE_DETECTED = "MOUSE_DETECTED"

    # Behavior-related events
    LOOKING_LEFT = "LOOKING_LEFT"
    LOOKING_RIGHT = "LOOKING_RIGHT"
    LOOKING_DOWN = "LOOKING_DOWN"
    STANDING = "STANDING"

    def __str__(self) -> str:
        """Return string representation of event type."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "EventType":
        """
        Create EventType from string.

        Args:
            value: String value of event type

        Returns:
            EventType instance

        Raises:
            ValueError: If value is not a valid event type
        """
        for event_type in cls:
            if event_type.value == value:
                return event_type
        raise ValueError(f"Invalid event type: {value}")


class EventSeverity(Enum):
    """Enum for event severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        """Return string representation of severity."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "EventSeverity":
        """
        Create EventSeverity from string.

        Args:
            value: String value of severity

        Returns:
            EventSeverity instance

        Raises:
            ValueError: If value is not a valid severity
        """
        for severity in cls:
            if severity.value == value:
                return severity
        raise ValueError(f"Invalid severity: {value}")
