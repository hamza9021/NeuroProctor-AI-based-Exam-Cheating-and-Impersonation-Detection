"""
Temporal module for event smoothing and stabilization.
"""

from .temporal_event import TemporalEvent, TemporalEventSequence, EventState
from .state import EventStateManager
from .tracker import EventTracker
from .window import SlidingWindow
from .strategies import (
    SmoothingStrategy,
    SlidingWindowStrategy,
    MajorityVotingStrategy,
    MinimumDurationStrategy,
    HybridStrategy,
)
from .smoother import TemporalSmoother

__all__ = [
    "TemporalEvent",
    "TemporalEventSequence",
    "EventState",
    "EventStateManager",
    "EventTracker",
    "SlidingWindow",
    "SmoothingStrategy",
    "SlidingWindowStrategy",
    "MajorityVotingStrategy",
    "MinimumDurationStrategy",
    "HybridStrategy",
    "TemporalSmoother",
]
