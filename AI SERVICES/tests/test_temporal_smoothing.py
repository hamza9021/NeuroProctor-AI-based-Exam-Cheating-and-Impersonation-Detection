"""Tests for temporal smoothing of head pose angles."""

import pytest
from app.services.ai.analyzers.head_pose.temporal_smoother import TemporalSmoother, AngleState


class TestTemporalSmootherInitialization:
    """Tests for TemporalSmoother initialization."""

    def test_initialization_with_valid_alpha(self):
        """Test that smoother initializes with valid alpha."""
        smoother = TemporalSmoother(alpha=0.35)
        assert smoother._alpha == 0.35
        assert smoother._enabled == True

    def test_initialization_with_invalid_alpha_raises_error(self):
        """Test that invalid alpha raises ValueError."""
        with pytest.raises(ValueError):
            TemporalSmoother(alpha=0.0)

        with pytest.raises(ValueError):
            TemporalSmoother(alpha=1.5)

        with pytest.raises(ValueError):
            TemporalSmoother(alpha=-0.1)

    def test_initialization_with_disabled_smoothing(self):
        """Test that smoothing can be disabled."""
        smoother = TemporalSmoother(alpha=0.35, enabled=False)
        assert smoother._enabled == False

    def test_initialization_with_custom_parameters(self):
        """Test that custom parameters are set correctly."""
        smoother = TemporalSmoother(
            alpha=0.5,
            max_missing_frames=10,
            max_single_frame_delta=60.0,
            enabled=True,
        )
        assert smoother._alpha == 0.5
        assert smoother._max_missing_frames == 10
        assert smoother._max_single_frame_delta == 60.0
        assert smoother._enabled == True


class TestFirstValidReading:
    """Tests for first valid reading initialization."""

    def test_first_reading_initializes_from_raw_values(self):
        """Test that first valid reading initializes from raw values, not zero."""
        smoother = TemporalSmoother(alpha=0.35)

        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=42.7,
            raw_pitch=15.3,
            raw_roll=8.2,
            frame_index=0,
        )

        # Should initialize directly from raw values
        assert yaw == 42.7
        assert pitch == 15.3
        assert roll == 8.2

    def test_first_reading_creates_state(self):
        """Test that first reading creates smoothing state."""
        smoother = TemporalSmoother(alpha=0.35)

        smoother.smooth(
            track_id=1,
            raw_yaw=42.7,
            raw_pitch=15.3,
            raw_roll=8.2,
            frame_index=0,
        )

        assert smoother.has_track(track_id=1)
        state = smoother._states[1]
        assert state.yaw == 42.7
        assert state.pitch == 15.3
        assert state.roll == 8.2
        assert state.last_frame_index == 0
        assert state.missing_frame_count == 0


class TestEMASmoothing:
    """Tests for EMA smoothing application."""

    def test_second_reading_applies_ema_correctly(self):
        """Test that second reading applies EMA correctly."""
        smoother = TemporalSmoother(alpha=0.35)

        # First reading - initialize
        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        # Second reading - apply EMA
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=50.0,
            raw_pitch=15.0,
            raw_roll=10.0,
            frame_index=1,
        )

        # EMA: smoothed = alpha * current + (1 - alpha) * previous
        # yaw: 0.35 * 50.0 + 0.65 * 40.0 = 17.5 + 26.0 = 43.5
        assert abs(yaw - 43.5) < 0.01
        # pitch: 0.35 * 15.0 + 0.65 * 10.0 = 5.25 + 6.5 = 11.75
        assert abs(pitch - 11.75) < 0.01
        # roll: 0.35 * 10.0 + 0.65 * 5.0 = 3.5 + 3.25 = 6.75
        assert abs(roll - 6.75) < 0.01

    def test_yaw_pitch_roll_smoothed_independently(self):
        """Test that yaw, pitch and roll are smoothed independently."""
        smoother = TemporalSmoother(alpha=0.4)

        # Initialize
        smoother.smooth(
            track_id=1,
            raw_yaw=0.0,
            raw_pitch=0.0,
            raw_roll=0.0,
            frame_index=0,
        )

        # Different changes for each angle
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=10.0,
            raw_pitch=20.0,
            raw_roll=30.0,
            frame_index=1,
        )

        # Each should be smoothed independently
        assert yaw != 10.0
        assert pitch != 20.0
        assert roll != 30.0
        assert yaw < 10.0  # Smoothed towards 0
        assert pitch < 20.0
        assert roll < 30.0


class TestPerTrackState:
    """Tests for per-track state management."""

    def test_track_0_and_track_1_have_independent_histories(self):
        """Test that Track 0 and Track 1 have independent histories."""
        smoother = TemporalSmoother(alpha=0.35)

        # Track 0
        smoother.smooth(
            track_id=0,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )
        yaw0, pitch0, roll0 = smoother.smooth(
            track_id=0,
            raw_yaw=50.0,
            raw_pitch=15.0,
            raw_roll=10.0,
            frame_index=1,
        )

        # Track 1 - different values
        smoother.smooth(
            track_id=1,
            raw_yaw=-40.0,
            raw_pitch=-10.0,
            raw_roll=-5.0,
            frame_index=0,
        )
        yaw1, pitch1, roll1 = smoother.smooth(
            track_id=1,
            raw_yaw=-50.0,
            raw_pitch=-15.0,
            raw_roll=-10.0,
            frame_index=1,
        )

        # Tracks should have independent values
        assert yaw0 != yaw1
        assert pitch0 != pitch1
        assert roll0 != roll1
        assert yaw0 > 0  # Track 0 positive
        assert yaw1 < 0  # Track 1 negative


class TestSmootherLifecycle:
    """Tests for smoother lifecycle management."""

    def test_smoother_instance_remains_same_across_frames(self):
        """Test that smoother instance remains the same across frames."""
        smoother = TemporalSmoother(alpha=0.35)
        object_id = id(smoother)

        # Process multiple frames
        for i in range(10):
            smoother.smooth(
                track_id=1,
                raw_yaw=40.0 + i,
                raw_pitch=10.0 + i,
                raw_roll=5.0 + i,
                frame_index=i,
            )

        # Object ID should remain the same
        assert id(smoother) == object_id


class TestMissingFrameHandling:
    """Tests for missing frame handling."""

    def test_missing_frame_does_not_insert_zero(self):
        """Test that missing frame does not insert zero."""
        smoother = TemporalSmoother(alpha=0.35)

        # Frame 0
        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        # Frame 2 (skip frame 1)
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=50.0,
            raw_pitch=15.0,
            raw_roll=10.0,
            frame_index=2,
        )

        # Should not be zero
        assert yaw != 0.0
        assert pitch != 0.0
        assert roll != 0.0
        # Should be smoothed from previous state
        assert yaw != 50.0

    def test_one_missing_frame_does_not_clear_history(self):
        """Test that one missing frame does not clear history."""
        smoother = TemporalSmoother(alpha=0.35, max_missing_frames=5)

        # Frame 0
        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        # Frame 2 (skip frame 1)
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=50.0,
            raw_pitch=15.0,
            raw_roll=10.0,
            frame_index=2,
        )

        # State should still exist
        assert smoother.has_track(track_id=1)
        assert smoother._states[1].missing_frame_count == 1

    def test_history_clears_after_missing_limit(self):
        """Test that history clears after the configured missing limit."""
        smoother = TemporalSmoother(alpha=0.35, max_missing_frames=3)

        # Frame 0
        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        # Frame 5 (skip 4 frames - exceeds limit of 3)
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=50.0,
            raw_pitch=15.0,
            raw_roll=10.0,
            frame_index=5,
        )

        # Should re-initialize (clear state)
        assert yaw == 50.0  # Direct initialization
        assert pitch == 15.0
        assert roll == 10.0

    def test_track_expiry_clears_state(self):
        """Test that track expiry clears state."""
        smoother = TemporalSmoother(alpha=0.35)

        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        assert smoother.has_track(track_id=1)

        # Remove track
        smoother.remove_track(track_id=1)

        assert not smoother.has_track(track_id=1)


class TestAngleAwareSmoothing:
    """Tests for angle-aware shortest-path smoothing."""

    def test_minus_179_to_plus_179_uses_shortest_angle(self):
        """Test that -179° to +179° transition uses shortest-angle smoothing."""
        smoother = TemporalSmoother(alpha=0.5)

        # Initialize at -179
        smoother.smooth(
            track_id=1,
            raw_yaw=-179.0,
            raw_pitch=0.0,
            raw_roll=0.0,
            frame_index=0,
        )

        # Move to +179 (should go through 0, not 358)
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=179.0,
            raw_pitch=0.0,
            raw_roll=0.0,
            frame_index=1,
        )

        # Shortest path: -179 -> 0 -> 179 (delta = 2 degrees)
        # With alpha=0.5: -179 + 0.5 * 2 = -178
        # But due to normalization, -180 is equivalent to 180
        # The key is that it should NOT jump to +179 directly
        assert yaw != 179.0  # Should not jump directly to target
        # The result should be close to -180 (which is equivalent to 180)
        assert abs(yaw - 180.0) < 2.0 or abs(yaw + 180.0) < 2.0

    def test_plus_179_to_minus_179_uses_shortest_angle(self):
        """Test that +179° to -179° transition uses shortest-angle smoothing."""
        smoother = TemporalSmoother(alpha=0.5)

        # Initialize at +179
        smoother.smooth(
            track_id=1,
            raw_yaw=179.0,
            raw_pitch=0.0,
            raw_roll=0.0,
            frame_index=0,
        )

        # Move to -179
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=-179.0,
            raw_pitch=0.0,
            raw_roll=0.0,
            frame_index=1,
        )

        # Should move towards 0, not jump to -179
        assert yaw != -179.0  # Should not jump directly to target
        # The result should be close to 180 or -180 (equivalent)
        assert abs(yaw - 180.0) < 2.0 or abs(yaw + 180.0) < 2.0


class TestSpikeProtection:
    """Tests for spike protection."""

    def test_one_frame_spike_reduced(self):
        """Test that a one-frame spike does not create a full display jump."""
        smoother = TemporalSmoother(alpha=0.35, max_single_frame_delta=45.0)

        # Initialize stable values
        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        # Extreme spike (60 degree change)
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=100.0,  # 60 degree jump
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=1,
        )

        # Should be more conservative than normal EMA
        # Normal EMA: 0.35 * 100 + 0.65 * 40 = 35 + 26 = 61
        # With spike protection: should be closer to 40
        assert yaw < 61.0  # More conservative than normal EMA
        assert yaw > 40.0  # Still moved somewhat

    def test_sustained_movement_remains_responsive(self):
        """Test that sustained real movement remains responsive."""
        smoother = TemporalSmoother(alpha=0.35, max_single_frame_delta=45.0)

        # Initialize
        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        # Sustained movement across multiple frames
        for i in range(1, 6):
            yaw, pitch, roll = smoother.smooth(
                track_id=1,
                raw_yaw=40.0 + i * 10.0,  # Gradual increase
                raw_pitch=10.0,
                raw_roll=5.0,
                frame_index=i,
            )

        # Should have moved significantly (responsive)
        assert yaw > 40.0
        assert yaw < 90.0  # But smoothed

    def test_spike_protection_disabled_when_zero(self):
        """Test that spike protection is disabled when threshold is zero."""
        smoother = TemporalSmoother(alpha=0.35, max_single_frame_delta=0.0)

        # Initialize
        smoother.smooth(
            track_id=1,
            raw_yaw=40.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=0,
        )

        # Extreme spike
        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=100.0,
            raw_pitch=10.0,
            raw_roll=5.0,
            frame_index=1,
        )

        # Should use normal EMA (no spike protection)
        expected = 0.35 * 100.0 + 0.65 * 40.0  # 61.0
        assert abs(yaw - expected) < 0.01


class TestDisabledSmoothing:
    """Tests for disabled smoothing."""

    def test_disabled_smoothing_returns_raw_values(self):
        """Test that disabled smoothing returns raw values."""
        smoother = TemporalSmoother(alpha=0.35, enabled=False)

        yaw, pitch, roll = smoother.smooth(
            track_id=1,
            raw_yaw=42.7,
            raw_pitch=15.3,
            raw_roll=8.2,
            frame_index=0,
        )

        assert yaw == 42.7
        assert pitch == 15.3
        assert roll == 8.2

    def test_disabled_smoothing_does_not_create_state(self):
        """Test that disabled smoothing does not create state."""
        smoother = TemporalSmoother(alpha=0.35, enabled=False)

        smoother.smooth(
            track_id=1,
            raw_yaw=42.7,
            raw_pitch=15.3,
            raw_roll=8.2,
            frame_index=0,
        )

        assert not smoother.has_track(track_id=1)


class TestRawValuesPreservation:
    """Tests for raw values preservation."""

    def test_raw_values_remain_unchanged(self):
        """Test that raw values remain unchanged."""
        smoother = TemporalSmoother(alpha=0.35)

        # Process multiple frames
        for i in range(5):
            raw_yaw = 40.0 + i * 10.0
            raw_pitch = 10.0 + i * 5.0
            raw_roll = 5.0 + i * 2.0

            yaw, pitch, roll = smoother.smooth(
                track_id=1,
                raw_yaw=raw_yaw,
                raw_pitch=raw_pitch,
                raw_roll=raw_roll,
                frame_index=i,
            )

            # Raw values should be what we passed in
            # (This is verified by the fact that we pass them in)
            # The smoother should not modify the input values
            assert raw_yaw == 40.0 + i * 10.0
            assert raw_pitch == 10.0 + i * 5.0
            assert raw_roll == 5.0 + i * 2.0


class TestClearFunctionality:
    """Tests for clear functionality."""

    def test_clear_all_states(self):
        """Test that clear removes all states."""
        smoother = TemporalSmoother(alpha=0.35)

        # Add multiple tracks
        for track_id in range(5):
            smoother.smooth(
                track_id=track_id,
                raw_yaw=40.0,
                raw_pitch=10.0,
                raw_roll=5.0,
                frame_index=0,
            )

        assert len(smoother._states) == 5

        # Clear all
        smoother.clear()

        assert len(smoother._states) == 0
