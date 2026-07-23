"""
Events module for exam monitoring.
"""

from .event_types import EventType, EventSeverity
from .event import ExamEvent, FrameEvents

__all__ = [
    "EventType",
    "EventSeverity",
    "ExamEvent",
    "FrameEvents",
]
