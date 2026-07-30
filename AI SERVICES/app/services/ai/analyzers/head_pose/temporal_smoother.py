"""Temporal smoothing for head pose angles using angle-aware EMA."""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AngleState:
    """Per-track smoothing state.

    Attributes:
        yaw: Smoothed yaw angle in degrees.
        pitch: Smoothed pitch angle in degrees.
        roll: Smoothed roll angle in degrees.
        last_frame_index: Frame index of last valid update.
        missing_frame_count: Number of consecutive missing frames.
        yaw_history: Last 3 raw yaw values for median filtering.
        pitch_history: Last 3 raw pitch values for median filtering.
        roll_history: Last 3 raw roll values for median filtering.
    """
    yaw: float
    pitch: float
    roll: float
    last_frame_index: int
    missing_frame_count: int = 0
    yaw_history: list = None
    pitch_history: list = None
    roll_history: list = None

    def __post_init__(self):
        if self.yaw_history is None:
            self.yaw_history = []
        if self.pitch_history is None:
            self.pitch_history = []
        if self.roll_history is None:
            self.roll_history = []


class TemporalSmoother:
    """Angle-aware exponential moving average smoother for head pose.
    
    Maintains independent smoothing state per DeepSORT track_id.
    Uses shortest-angle interpolation to handle -180°/+180° transitions.
    """

    def __init__(
        self,
        alpha: float = 0.35,
        max_missing_frames: int = 5,
        max_single_frame_delta: float = 45.0,
        enabled: bool = True,
    ):
        """Initialize temporal smoother.

        Args:
            alpha: EMA smoothing factor (0.0 < alpha <= 1.0). Higher = more responsive.
            max_missing_frames: Maximum consecutive missing frames before clearing state.
            max_single_frame_delta: Maximum allowed single-frame angular change (degrees).
            enabled: Whether smoothing is enabled.

        Raises:
            ValueError: If alpha is not in valid range.
        """
        if not (0.0 < alpha <= 1.0):
            raise ValueError(f"alpha must be in (0.0, 1.0], got {alpha}")

        self._alpha = alpha
        self._max_missing_frames = max_missing_frames
        self._max_single_frame_delta = max_single_frame_delta
        self._enabled = enabled
        self._states: dict[int, AngleState] = {}

        logger.info(
            "TemporalSmoother initialized: alpha=%.2f, max_missing_frames=%d, "
            "max_single_frame_delta=%.1f, enabled=%s, object_id=%d",
            alpha, max_missing_frames, max_single_frame_delta, enabled, id(self),
        )

    def smooth(
        self,
        track_id: int,
        raw_yaw: float,
        raw_pitch: float,
        raw_roll: float,
        frame_index: int,
    ) -> tuple[float, float, float]:
        """Apply temporal smoothing to raw angles.

        Args:
            track_id: DeepSORT track ID.
            raw_yaw: Raw yaw angle in degrees.
            raw_pitch: Raw pitch angle in degrees.
            raw_roll: Raw roll angle in degrees.
            frame_index: Current frame index.

        Returns:
            Tuple of (smoothed_yaw, smoothed_pitch, smoothed_roll).
        """
        if not self._enabled:
            return raw_yaw, raw_pitch, raw_roll

        # Check if track exists and handle missing frames
        if track_id in self._states:
            state = self._states[track_id]
            frame_gap = frame_index - state.last_frame_index

            # Handle missing frames
            if frame_gap > 1:
                state.missing_frame_count += frame_gap - 1

                # Clear state if missing too many frames
                if state.missing_frame_count > self._max_missing_frames:
                    logger.debug(
                        "track_id=%d: clearing state after %d missing frames",
                        track_id, state.missing_frame_count,
                    )
                    del self._states[track_id]
                    # Initialize fresh
                    return self._initialize_track(track_id, raw_yaw, raw_pitch, raw_roll, frame_index)
                else:
                    logger.debug(
                        "track_id=%d: preserving state through %d missing frames",
                        track_id, state.missing_frame_count,
                    )
            else:
                # Reset missing frame count on valid frame
                state.missing_frame_count = 0
        else:
            # New track - initialize directly from raw values
            return self._initialize_track(track_id, raw_yaw, raw_pitch, raw_roll, frame_index)

        # Apply angle-aware EMA smoothing with median outlier check
        state = self._states[track_id]

        # Update history buffers (keep last 3 values)
        state.yaw_history.append(raw_yaw)
        state.pitch_history.append(raw_pitch)
        state.roll_history.append(raw_roll)
        if len(state.yaw_history) > 3:
            state.yaw_history.pop(0)
        if len(state.pitch_history) > 3:
            state.pitch_history.pop(0)
        if len(state.roll_history) > 3:
            state.roll_history.pop(0)

        # Apply median outlier check if we have 3 samples
        filtered_yaw = self._apply_median_filter(state.yaw_history, raw_yaw)
        filtered_pitch = self._apply_median_filter(state.pitch_history, raw_pitch)
        filtered_roll = self._apply_median_filter(state.roll_history, raw_roll)

        # Use filtered values for smoothing
        smoothed_yaw = self._smooth_angle(state.yaw, filtered_yaw, self._alpha)
        smoothed_pitch = self._smooth_angle(state.pitch, filtered_pitch, self._alpha)
        smoothed_roll = self._smooth_angle(state.roll, filtered_roll, self._alpha)

        # Optional spike protection
        if self._max_single_frame_delta > 0:
            smoothed_yaw = self._apply_spike_protection(state.yaw, filtered_yaw, smoothed_yaw, self._alpha)
            smoothed_pitch = self._apply_spike_protection(state.pitch, filtered_pitch, smoothed_pitch, self._alpha)
            smoothed_roll = self._apply_spike_protection(state.roll, filtered_roll, smoothed_roll, self._alpha)

        # Capture previous values for logging before updating state
        previous_yaw = state.yaw
        previous_pitch = state.pitch
        previous_roll = state.roll

        # Update state
        state.yaw = smoothed_yaw
        state.pitch = smoothed_pitch
        state.roll = smoothed_roll
        state.last_frame_index = frame_index

        logger.debug(
            "[HEAD-POSE SMOOTHING] "
            "frame=%d track_id=%d "
            "previous_before_update_yaw=%.2f previous_before_update_pitch=%.2f previous_before_update_roll=%.2f "
            "raw_current_yaw=%.2f raw_current_pitch=%.2f raw_current_roll=%.2f "
            "smoothed_after_update_yaw=%.2f smoothed_after_update_pitch=%.2f smoothed_after_update_roll=%.2f "
            "alpha=%.2f history_exists=True object_id=%d",
            frame_index, track_id,
            previous_yaw, previous_pitch, previous_roll,
            raw_yaw, raw_pitch, raw_roll,
            smoothed_yaw, smoothed_pitch, smoothed_roll,
            self._alpha, id(self),
        )

        return smoothed_yaw, smoothed_pitch, smoothed_roll

    def _initialize_track(
        self,
        track_id: int,
        raw_yaw: float,
        raw_pitch: float,
        raw_roll: float,
        frame_index: int,
    ) -> tuple[float, float, float]:
        """Initialize smoothing state for a new track.

        Args:
            track_id: DeepSORT track ID.
            raw_yaw: Raw yaw angle in degrees.
            raw_pitch: Raw pitch angle in degrees.
            raw_roll: Raw roll angle in degrees.
            frame_index: Current frame index.

        Returns:
            Tuple of (yaw, pitch, roll) initialized from raw values.
        """
        self._states[track_id] = AngleState(
            yaw=raw_yaw,
            pitch=raw_pitch,
            roll=raw_roll,
            last_frame_index=frame_index,
            missing_frame_count=0,
        )

        logger.debug(
            "[HEAD-POSE SMOOTHING] "
            "frame=%d track_id=%d "
            "raw_yaw=%.2f raw_pitch=%.2f raw_roll=%.2f "
            "smoothed_yaw=%.2f smoothed_pitch=%.2f smoothed_roll=%.2f "
            "alpha=%.2f history_exists=False (initialized) object_id=%d",
            frame_index, track_id,
            raw_yaw, raw_pitch, raw_roll,
            raw_yaw, raw_pitch, raw_roll,
            self._alpha, id(self),
        )

        return raw_yaw, raw_pitch, raw_roll

    def _smooth_angle(self, previous: float, current: float, alpha: float) -> float:
        """Apply angle-aware EMA smoothing using shortest-angle interpolation.

        Args:
            previous: Previous angle in degrees.
            current: Current angle in degrees.
            alpha: EMA smoothing factor.

        Returns:
            Smoothed angle in degrees.
        """
        # Compute shortest angular difference
        diff = current - previous
        # Normalize to [-180, 180]
        diff = (diff + 180) % 360 - 180
        smoothed = previous + alpha * diff
        # Normalize result to [-180, 180]
        smoothed = (smoothed + 180) % 360 - 180
        return smoothed

    def _apply_median_filter(self, history: list, current: float) -> float:
        """Apply median-based outlier rejection.

        If the current value is an outlier compared to the median of history,
        use the median instead. Otherwise use the current value.

        Args:
            history: List of recent angle values (up to 3).
            current: Current angle value.

        Returns:
            Filtered angle value.
        """
        if len(history) < 3:
            return current

        import numpy as np

        # Compute median of history
        median = np.median(history)

        # Check if current is an outlier (more than 30 degrees from median)
        delta = abs((current - median + 180.0) % 360.0 - 180.0)
        if delta > 30.0:
            logger.debug(
                "Median filter: current=%.1f is outlier (delta=%.1f > 30), using median=%.1f",
                current, delta, median,
            )
            return median

        return current

    def _apply_spike_protection(
        self,
        previous: float,
        current: float,
        smoothed: float,
        alpha: float,
    ) -> float:
        """Apply optional spike protection for extreme single-frame changes.

        If the angular difference exceeds the threshold, use a more conservative
        smoothing factor to reduce the impact of the spike.

        Args:
            previous: Previous angle in degrees.
            current: Current angle in degrees.
            smoothed: Already smoothed angle.
            alpha: Original EMA smoothing factor.

        Returns:
            Angle with spike protection applied.
        """
        delta = abs((current - previous + 180.0) % 360.0 - 180.0)
        
        if delta > self._max_single_frame_delta:
            # Use more conservative smoothing for potential spikes
            conservative_alpha = alpha * 0.5
            logger.debug(
                "Spike detected: delta=%.1f > threshold=%.1f, using conservative alpha=%.2f",
                delta, self._max_single_frame_delta, conservative_alpha,
            )
            return previous + conservative_alpha * ((current - previous + 180.0) % 360.0 - 180.0)
        
        return smoothed

    def remove_track(self, track_id: int) -> None:
        """Remove smoothing state for a track.

        Args:
            track_id: DeepSORT track ID to remove.
        """
        if track_id in self._states:
            del self._states[track_id]
            logger.debug("track_id=%d: smoothing state removed", track_id)

    def has_track(self, track_id: int) -> bool:
        """Check if a track has smoothing state.

        Args:
            track_id: DeepSORT track ID.

        Returns:
            True if track has state, False otherwise.
        """
        return track_id in self._states

    def clear(self) -> None:
        """Clear all smoothing state."""
        self._states.clear()
        logger.debug("All smoothing state cleared")
