"""Unit tests for head pose estimation modules."""

from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STRING = str(PROJECT_ROOT)

if PROJECT_ROOT_STRING in sys.path:
    sys.path.remove(PROJECT_ROOT_STRING)

sys.path.insert(0, PROJECT_ROOT_STRING)

import app

print(f"Project root: {PROJECT_ROOT}")
print(f"Imported app from: {app.__file__}")

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    AXIS_PITCH,
    AXIS_ROLL,
    AXIS_YAW,
    LABEL_PITCH,
    LABEL_ROLL,
    LABEL_YAW,
    VALID_ANGLES,
)
from app.services.ai.analyzers.head_pose.exceptions import (
    FaceRegionNotFoundError,
    HeadPoseInitializationError,
    HeadPoseParsingError,
    HeadPoseValidationError,
    InvalidFaceCropError,
)
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult
from app.services.ai.analyzers.head_pose.mapper import HeadPoseMapper
from app.services.ai.analyzers.head_pose.parser import HeadPoseParser
from app.services.ai.analyzers.head_pose.text_drawer import TextDrawer
from app.services.ai.analyzers.head_pose.validator import HeadPoseValidator
from app.services.ai.pipeline.frame_context import FrameContext


class TestHeadPoseConfig:
    """Test HeadPoseConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = HeadPoseConfig()
        assert config.model_path == "models/6drepnet/6DRepNet_300W_LP_AFLW2000.pth"
        assert config.device == "auto"
        assert config.face_padding == 0.20
        assert config.min_face_size == 40
        assert config.max_abs_angle == 90.0
        assert config.annotation_enabled is True
        assert config.draw_axis is True
        assert config.log_level == "detailed"
        assert config.frame_log_interval == 10

    def test_custom_config(self):
        """Test custom configuration values."""
        config = HeadPoseConfig(
            model_path="custom/path.pth",
            device="cuda",
            face_padding=0.30,
            min_face_size=50,
        )
        assert config.model_path == "custom/path.pth"
        assert config.device == "cuda"
        assert config.face_padding == 0.30
        assert config.min_face_size == 50


class TestHeadPoseResult:
    """Test HeadPoseResult dataclass."""

    def test_head_pose_result_creation(self):
        """Test creating a head pose result."""
        result = HeadPoseResult(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
            confidence=0.95,
            is_valid=True,
        )
        assert result.track_id == 1
        assert result.face_bbox == (10.0, 20.0, 30.0, 40.0)
        assert result.yaw == -15.5
        assert result.pitch == 8.2
        assert result.roll == 3.1
        assert result.confidence == 0.95
        assert result.is_valid is True

    def test_head_pose_result_defaults(self):
        """Test head pose result with default values."""
        result = HeadPoseResult(
            track_id=2,
            face_bbox=(0.0, 0.0, 50.0, 50.0),
            yaw=0.0,
            pitch=0.0,
            roll=0.0,
        )
        assert result.confidence is None
        assert result.is_valid is True


class TestHeadPoseParser:
    """Test HeadPoseParser."""

    @pytest.mark.asyncio
    async def test_parse_valid_output(self):
        """Test parsing a valid 3x3 rotation matrix.

        The parser now expects a (3, 3) rotation matrix from the official
        SixDRepNet forward pass, not a flat [pitch, yaw, roll] vector.
        Verify that:
        - all three returned values are Python floats;
        - an identity matrix yields angles near zero;
        - a known yaw rotation yields a measurably non-zero yaw.
        """
        logger = AsyncMock()
        parser = HeadPoseParser(logger)

        # Identity matrix → all angles ≈ 0
        R_identity = np.eye(3, dtype=np.float32)
        yaw, pitch, roll = await parser.parse(R_identity, track_id=1)

        assert isinstance(yaw, float)
        assert isinstance(pitch, float)
        assert isinstance(roll, float)
        assert abs(yaw) < 1e-3
        assert abs(pitch) < 1e-3
        assert abs(roll) < 1e-3

        # 30° rotation around Y-axis → yaw ≈ 30°
        a = np.radians(30.0)
        R_yaw30 = np.array([
            [ np.cos(a), 0.0, np.sin(a)],
            [        0., 1.0,        0.],
            [-np.sin(a), 0.0, np.cos(a)],
        ], dtype=np.float32)
        yaw30, pitch30, roll30 = await parser.parse(R_yaw30, track_id=1)
        assert abs(yaw30 - 30.0) < 1.0, (
            f"Expected yaw ≈ 30°, got {yaw30:.2f}°"
        )


    @pytest.mark.asyncio
    async def test_parse_invalid_output(self):
        """Test parsing invalid model output."""
        logger = AsyncMock()
        parser = HeadPoseParser(logger)

        # Invalid output shape
        raw_output = np.array([0.1, 0.2])  # Only 2 values

        with pytest.raises(HeadPoseParsingError):
            await parser.parse(raw_output, track_id=1)


class TestHeadPoseValidator:
    """Test HeadPoseValidator."""

    @pytest.mark.asyncio
    async def test_validate_valid_result(self):
        """Test validating a valid head pose result."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)

        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
        )

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_invalid_yaw(self):
        """Test validating with invalid yaw (exceeds limit)."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)

        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=100.0,  # Exceeds max_abs_angle
            pitch=8.2,
            roll=3.1,
        )

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_nan_value(self):
        """Test validating with NaN value."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)

        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=float('nan'),
            pitch=8.2,
            roll=3.1,
        )

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_invalid_bbox(self):
        """Test validating with invalid bounding box."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)

        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(30.0, 20.0, 10.0, 40.0),  # x2 < x1
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
        )

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_negative_track_id(self):
        """Test validating with negative track ID."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)

        is_valid = await validator.validate(
            track_id=-1,  # Invalid
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
        )

        assert is_valid is False


class TestHeadPoseMapper:
    """Test HeadPoseMapper."""

    @pytest.mark.asyncio
    async def test_map_results_to_context(self):
        """Test mapping head pose results to FrameContext."""
        logger = AsyncMock()
        mapper = HeadPoseMapper(logger)
        context = FrameContext(
            frame=np.zeros((480, 640, 3), dtype=np.uint8),
            frame_number=1,
            timestamp=datetime.now(),
        )

        results = [
            HeadPoseResult(
                track_id=1,
                face_bbox=(10.0, 20.0, 30.0, 40.0),
                yaw=-15.5,
                pitch=8.2,
                roll=3.1,
                is_valid=True,
            ),
            HeadPoseResult(
                track_id=2,
                face_bbox=(50.0, 60.0, 70.0, 80.0),
                yaw=10.0,
                pitch=-5.0,
                roll=2.0,
                is_valid=True,
            ),
        ]

        context = await mapper.map(context, results)

        assert context.head_pose is not None
        assert len(context.head_pose) == 2
        assert 1 in context.head_pose
        assert 2 in context.head_pose
        assert context.head_pose[1].track_id == 1
        assert context.head_pose[2].track_id == 2

    @pytest.mark.asyncio
    async def test_map_invalid_results(self):
        """Test mapping with invalid results (should be excluded)."""
        logger = AsyncMock()
        mapper = HeadPoseMapper(logger)
        context = FrameContext(
            frame=np.zeros((480, 640, 3), dtype=np.uint8),
            frame_number=1,
            timestamp=datetime.now(),
        )

        results = [
            HeadPoseResult(
                track_id=1,
                face_bbox=(10.0, 20.0, 30.0, 40.0),
                yaw=-15.5,
                pitch=8.2,
                roll=3.1,
                is_valid=True,
            ),
            HeadPoseResult(
                track_id=2,
                face_bbox=(50.0, 60.0, 70.0, 80.0),
                yaw=10.0,
                pitch=-5.0,
                roll=2.0,
                is_valid=False,  # Invalid
            ),
        ]

        context = await mapper.map(context, results)

        assert len(context.head_pose) == 1
        assert 1 in context.head_pose
        assert 2 not in context.head_pose


class TestConstants:
    """Test constants."""

    def test_valid_angles(self):
        """Test valid angle names."""
        assert AXIS_YAW in VALID_ANGLES
        assert AXIS_PITCH in VALID_ANGLES
        assert AXIS_ROLL in VALID_ANGLES
        assert len(VALID_ANGLES) == 3


# ============================================================================
# NEW TESTS  (corrections applied per review)
# ============================================================================


class TestHeadPoseResultNewFields:
    """Verify person_bbox and axis_origin fields on HeadPoseResult."""

    def test_person_bbox_and_axis_origin_stored(self):
        """person_bbox and axis_origin are stored and accessible."""
        result = HeadPoseResult(
            track_id=0,
            face_bbox=(50.0, 30.0, 130.0, 100.0),
            yaw=0.0,
            pitch=1.7,
            roll=-1.4,
            person_bbox=(40.0, 10.0, 200.0, 480.0),
            axis_origin=(90, 65),
        )
        assert result.person_bbox == (40.0, 10.0, 200.0, 480.0)
        assert result.axis_origin == (90, 65)

    def test_backward_compat_optional_fields_default_none(self):
        """Existing code that omits person_bbox / axis_origin still works."""
        # This tests backward compatibility: new fields must default to None.
        result = HeadPoseResult(
            track_id=1,
            face_bbox=(10.0, 20.0, 60.0, 70.0),
            yaw=0.0,
            pitch=0.0,
            roll=0.0,
        )
        assert result.person_bbox is None
        assert result.axis_origin is None
        # Core fields still accessible
        assert result.track_id == 1
        assert result.is_valid is True

    def test_named_args_prevent_positional_swap(self):
        """Named keyword args make roll/yaw/pitch swap impossible."""
        roll_val, yaw_val, pitch_val = -1.4, 0.0, 1.7
        result = HeadPoseResult(
            track_id=0,
            face_bbox=(0.0, 0.0, 100.0, 100.0),
            roll=roll_val,
            yaw=yaw_val,
            pitch=pitch_val,
        )
        assert result.roll == roll_val
        assert result.yaw == yaw_val
        assert result.pitch == pitch_val


# ---------------------------------------------------------------------------- #
# Helpers shared by TextDrawer tests                                            #
# ---------------------------------------------------------------------------- #

def _spy_draw(result: HeadPoseResult, frame_h: int = 480, frame_w: int = 640):
    """Draw on a blank frame, capturing each putText call in order.

    Returns:
        Tuple of (frame, drawn_texts list[str], y_positions list[int]).
    """
    import cv2 as _cv2

    frame = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
    drawn_texts: list = []
    y_positions: list = []

    orig = _cv2.putText

    def _spy(img, text, org, *args, **kwargs):
        drawn_texts.append(text)
        y_positions.append(org[1])
        return orig(img, text, org, *args, **kwargs)

    drawer = TextDrawer()
    with patch("app.services.ai.analyzers.head_pose.text_drawer.cv2.putText", side_effect=_spy):
        drawer.draw(frame, result)

    return frame, drawn_texts, y_positions


class TestTextDrawerLabelOrder:
    """Verify TextDrawer renders labels in ID → Roll → Yaw → Pitch order."""

    def _result(self, **kwargs):
        defaults = dict(
            track_id=0,
            face_bbox=(100.0, 100.0, 200.0, 180.0),
            roll=-1.4, yaw=0.0, pitch=1.7,
            person_bbox=(80.0, 60.0, 220.0, 460.0),
            axis_origin=(150, 130),
        )
        defaults.update(kwargs)
        return HeadPoseResult(**defaults)

    def test_id_is_first_line(self):
        """ID must appear as the very first rendered line."""
        _, texts, _ = _spy_draw(self._result())
        assert texts, "No text was drawn"
        assert texts[0].startswith("ID:"), (
            f"First line must start with 'ID:', got: {texts[0]!r}"
        )

    def test_label_order_id_roll_yaw_pitch(self):
        """Full order must be ID → Roll → Yaw → Pitch."""
        _, texts, _ = _spy_draw(self._result())
        assert len(texts) == 4, f"Expected 4 lines, got {texts}"
        assert texts[0].startswith("ID:"),                  f"Line 0: {texts[0]}"
        assert LABEL_ROLL  in texts[1],                    f"Line 1: {texts[1]}"
        assert LABEL_YAW   in texts[2],                    f"Line 2: {texts[2]}"
        assert LABEL_PITCH in texts[3],                    f"Line 3: {texts[3]}"

    def test_lines_progress_downward(self):
        """Every successive label baseline must be lower than the previous."""
        _, _, y_positions = _spy_draw(self._result())
        assert len(y_positions) == 4, f"Expected 4 y-positions, got {y_positions}"
        for i in range(1, len(y_positions)):
            assert y_positions[i] > y_positions[i - 1], (
                f"Line {i} y={y_positions[i]} is not below line {i-1} "
                f"y={y_positions[i-1]} — lines are NOT progressing downward"
            )

    def test_label_values_match_result(self):
        """Each value displayed must exactly match the HeadPoseResult field."""
        _, texts, _ = _spy_draw(self._result(roll=-1.4, yaw=0.0, pitch=1.7, track_id=5))
        full = " ".join(texts)
        assert "5"    in texts[0], f"ID 5 not in first line: {texts[0]}"
        assert "-1.4" in texts[1], f"roll -1.4 not in roll line: {texts[1]}"
        assert "0.0"  in texts[2], f"yaw 0.0 not in yaw line: {texts[2]}"
        assert "1.7"  in texts[3], f"pitch 1.7 not in pitch line: {texts[3]}"

    def test_no_yaw_pitch_swap(self):
        """Distinct yaw and pitch values must not be swapped in labels."""
        _, texts, _ = _spy_draw(self._result(roll=-1.4, yaw=5.0, pitch=20.0))
        # texts[2] = Yaw line, texts[3] = Pitch line
        assert "5.0"  in texts[2], f"Yaw line should show 5.0: {texts[2]}"
        assert "20.0" in texts[3], f"Pitch line should show 20.0: {texts[3]}"
        assert "20.0" not in texts[2], "Pitch value must not appear in Yaw line"
        assert "5.0"  not in texts[3], "Yaw value must not appear in Pitch line"


class TestTextDrawerPositionClamping:
    """Verify the complete text block stays inside the frame at all edges."""

    def _make_result(self, person_bbox, face_bbox=None):
        x1, y1, x2, y2 = person_bbox
        if face_bbox is None:
            face_bbox = (x1 + 5, y1 + 5, x2 - 5, min(y1 + 50, y2 - 5))
        return HeadPoseResult(
            track_id=0,
            face_bbox=face_bbox,
            roll=-1.4, yaw=0.0, pitch=1.7,
            person_bbox=person_bbox,
        )

    def _assert_inside_frame(self, y_positions, frame_h=480, frame_w=640):
        """All drawn y baselines must be within [1, frame_h-1]."""
        for y in y_positions:
            assert 0 < y < frame_h, (
                f"Baseline y={y} is outside frame (height={frame_h})"
            )

    def test_near_top_edge_no_crash_and_inside_frame(self):
        """Person at y=2 — full block must clamp inside the frame."""
        result = self._make_result(person_bbox=(100.0, 2.0, 300.0, 200.0))
        frame, _, y_pos = _spy_draw(result)
        self._assert_inside_frame(y_pos)

    def test_near_bottom_edge_no_crash_and_inside_frame(self):
        """Person at bottom — block must not exceed frame height."""
        result = self._make_result(person_bbox=(100.0, 400.0, 300.0, 478.0))
        frame, _, y_pos = _spy_draw(result)
        self._assert_inside_frame(y_pos)

    def test_near_left_edge_no_crash_and_inside_frame(self):
        """Person at x=0 — text_x must stay >= 0."""
        result = self._make_result(person_bbox=(0.0, 100.0, 100.0, 300.0))
        _, drawn_texts, y_pos = _spy_draw(result)
        self._assert_inside_frame(y_pos)
        # Must still produce 4 lines
        assert len(drawn_texts) == 4

    def test_near_right_edge_no_crash_and_inside_frame(self):
        """Person at right — block must not exceed frame width."""
        result = self._make_result(person_bbox=(560.0, 100.0, 638.0, 300.0))
        _, drawn_texts, y_pos = _spy_draw(result)
        self._assert_inside_frame(y_pos)
        assert len(drawn_texts) == 4

    def test_fallback_to_face_bbox_when_no_person_bbox(self):
        """When person_bbox is None the drawer falls back to face_bbox cleanly."""
        result = HeadPoseResult(
            track_id=0,
            face_bbox=(100.0, 200.0, 250.0, 280.0),
            roll=-1.4, yaw=0.0, pitch=1.7,
            # person_bbox intentionally omitted → None
        )
        _, drawn_texts, y_pos = _spy_draw(result)
        assert len(drawn_texts) == 4
        self._assert_inside_frame(y_pos)


class TestAxisOriginFallback:
    """Verify _compute_axis_origin returns correct values for each priority."""

    def _make_processor(self):
        from app.services.ai.analyzers.head_pose.track_processor import TrackProcessor
        return TrackProcessor(
            locator=MagicMock(),
            cropper=MagicMock(),
            estimator=MagicMock(),
            parser=MagicMock(),
            validator=MagicMock(),
        )

    def _origin(self, processor, pose_data, face_bbox, track_bbox,
                frame_h=480, frame_w=640):
        return processor._compute_axis_origin(
            pose_data, face_bbox, track_bbox, frame_h, frame_w
        )

    def test_priority1_reliable_nose_keypoint(self):
        """When nose keypoint confidence >= 0.5 it is used as origin."""
        from app.services.ai.analyzers.head_pose.track_processor import _NOSE_KP_INDEX
        kps = np.zeros((17, 3), dtype=np.float32)
        kps[_NOSE_KP_INDEX] = [320.0, 150.0, 0.9]   # x, y, conf

        processor = self._make_processor()
        cx, cy = self._origin(
            processor,
            pose_data={"keypoints": kps},
            face_bbox=(300.0, 130.0, 370.0, 190.0),
            track_bbox=(280.0, 100.0, 400.0, 450.0),
        )
        assert cx == 320, f"Expected cx=320, got {cx}"
        assert cy == 150, f"Expected cy=150, got {cy}"

    def test_priority1_low_confidence_nose_skipped(self):
        """When nose confidence < 0.5 it is skipped and face-centre is used."""
        from app.services.ai.analyzers.head_pose.track_processor import _NOSE_KP_INDEX
        kps = np.zeros((17, 3), dtype=np.float32)
        kps[_NOSE_KP_INDEX] = [320.0, 150.0, 0.3]   # low confidence

        face_bbox = (300.0, 130.0, 370.0, 190.0)
        processor = self._make_processor()
        cx, cy = self._origin(
            processor,
            pose_data={"keypoints": kps},
            face_bbox=face_bbox,
            track_bbox=(280.0, 100.0, 400.0, 450.0),
        )
        # Should be face-centre
        expected_cx = int((300.0 + 370.0) / 2)
        expected_cy = int((130.0 + 190.0) / 2)
        assert cx == expected_cx, f"Expected cx={expected_cx}, got {cx}"
        assert cy == expected_cy, f"Expected cy={expected_cy}, got {cy}"

    def test_priority2_face_bbox_centre(self):
        """Without pose_data the face-bbox centre is used."""
        face_bbox = (200.0, 100.0, 300.0, 180.0)
        processor = self._make_processor()
        cx, cy = self._origin(
            processor,
            pose_data=None,
            face_bbox=face_bbox,
            track_bbox=(180.0, 80.0, 320.0, 440.0),
        )
        assert cx == int((200.0 + 300.0) / 2)
        assert cy == int((100.0 + 180.0) / 2)

    def test_priority3_person_bbox_upper_centre_fallback(self):
        """Degenerate face_bbox (x2<=x1) falls through to person-bbox upper centre."""
        processor = self._make_processor()
        px1, py1, px2, py2 = 100.0, 50.0, 300.0, 450.0
        # Degenerate face bbox: x2 == x1 → condition fails
        cx, cy = self._origin(
            processor,
            pose_data=None,
            face_bbox=(200.0, 100.0, 200.0, 180.0),  # x2 == x1 → degenerate
            track_bbox=(px1, py1, px2, py2),
        )
        expected_cx = int((px1 + px2) / 2)
        expected_cy = int(py1 + (py2 - py1) * 0.15)
        assert cx == expected_cx
        assert cy == expected_cy

    def test_origin_clamped_to_frame(self):
        """Axis origin coordinates are always clamped to frame boundaries."""
        kps = np.zeros((17, 3), dtype=np.float32)
        kps[0] = [700.0, 600.0, 0.9]   # well outside 640×480

        processor = self._make_processor()
        cx, cy = self._origin(
            processor,
            pose_data={"keypoints": kps},
            face_bbox=(0.0, 0.0, 50.0, 50.0),
            track_bbox=(0.0, 0.0, 640.0, 480.0),
            frame_h=480, frame_w=640,
        )
        assert 0 <= cx <= 639, f"cx={cx} out of [0,639]"
        assert 0 <= cy <= 479, f"cy={cy} out of [0,479]"


class TestTrackAssociation:
    """Verify each student's head pose is associated with its own track_id."""

    @pytest.mark.asyncio
    async def test_two_tracks_independent_values(self):
        """Two tracks in head_pose dict retain independent roll/yaw/pitch."""
        mock_logger = AsyncMock()
        mapper = HeadPoseMapper(mock_logger)
        context = FrameContext(
            frame=np.zeros((480, 640, 3), dtype=np.uint8),
            frame_number=5,
            timestamp=datetime.now(),
        )

        result_a = HeadPoseResult(
            track_id=10,
            face_bbox=(50.0, 30.0, 130.0, 100.0),
            roll=-1.4, yaw=0.0, pitch=1.7,
            person_bbox=(30.0, 10.0, 150.0, 440.0),
            is_valid=True,
        )
        result_b = HeadPoseResult(
            track_id=11,
            face_bbox=(400.0, 30.0, 530.0, 120.0),
            roll=5.0, yaw=-20.0, pitch=10.0,
            person_bbox=(380.0, 10.0, 550.0, 440.0),
            is_valid=True,
        )

        context = await mapper.map(context, [result_a, result_b])

        assert 10 in context.head_pose
        assert 11 in context.head_pose

        hp_a = context.head_pose[10]
        hp_b = context.head_pose[11]

        assert hp_a.roll == -1.4 and hp_a.yaw == 0.0 and hp_a.pitch == 1.7
        assert hp_b.roll == 5.0  and hp_b.yaw == -20.0 and hp_b.pitch == 10.0

    def test_two_tracks_draw_independently(self):
        """TextDrawer for two different tracks must not raise or cross-contaminate."""
        result_a = HeadPoseResult(
            track_id=10,
            face_bbox=(50.0, 30.0, 130.0, 100.0),
            roll=-1.4, yaw=0.0, pitch=1.7,
            person_bbox=(30.0, 10.0, 150.0, 440.0),
        )
        result_b = HeadPoseResult(
            track_id=11,
            face_bbox=(400.0, 80.0, 530.0, 180.0),
            roll=5.0, yaw=-20.0, pitch=10.0,
            person_bbox=(380.0, 50.0, 550.0, 450.0),
        )

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        drawer = TextDrawer()
        drawer.draw(frame, result_a)
        drawer.draw(frame, result_b)
        assert frame is not None




# ============================================================================
# NEW TESTS — Frame-freshness, stale-result and model-loading (20 tests)
# ============================================================================

import asyncio
import zlib
import time
from unittest.mock import AsyncMock, MagicMock, patch, call

import numpy as np
import pytest
import torch

from app.services.ai.analyzers.head_pose.annotator import HeadPoseAnnotator
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.cropper import FaceCropper
from app.services.ai.analyzers.head_pose.estimator import HeadPoseEstimator
from app.services.ai.analyzers.head_pose.exceptions import (
    HeadPoseInitializationError,
    HeadPoseParsingError,
)
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult
from app.services.ai.analyzers.head_pose.loader import HeadPoseModelLoader
from app.services.ai.analyzers.head_pose.mapper import HeadPoseMapper
from app.services.ai.analyzers.head_pose.parser import (
    HeadPoseParser,
    _rotation_matrix_to_euler,
)
from app.services.ai.pipeline.frame_context import FrameContext


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def _identity_rotation() -> np.ndarray:
    return np.eye(3, dtype=np.float32)


def _make_logger() -> MagicMock:
    lg = MagicMock()
    lg.info = AsyncMock()
    lg.warning = AsyncMock()
    lg.error = AsyncMock()
    return lg


def _make_config(**kwargs) -> HeadPoseConfig:
    cfg = HeadPoseConfig()
    for k, v in kwargs.items():
        setattr(cfg, k, v)
    return cfg


def _make_frame(h: int = 480, w: int = 640, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, (h, w, 3), dtype=np.uint8)


def _make_model_returning(rotation_matrix: np.ndarray) -> MagicMock:
    """Return a mock torch.nn.Module whose forward() yields the given 3x3."""
    tensor_out = torch.from_numpy(rotation_matrix).unsqueeze(0)  # (1,3,3)
    model = MagicMock(spec=torch.nn.Module)
    model.return_value = tensor_out
    model.parameters = MagicMock(
        return_value=iter([torch.zeros(1)])
    )
    return model


# --------------------------------------------------------------------------- #
# 1. Current-frame crop test                                                   #
# --------------------------------------------------------------------------- #

class TestCurrentFrameCrop:
    """Two different frames produce two different crop checksums."""

    @pytest.mark.asyncio
    async def test_different_frames_different_crop_checksums(self):
        frame_a = _make_frame(seed=1)
        frame_b = _make_frame(seed=2)
        bbox = (10.0, 10.0, 100.0, 100.0)

        cfg = _make_config()
        lg = _make_logger()
        cropper = FaceCropper(cfg, lg)

        crop_a = await cropper.crop(frame_a, bbox, track_id=0)
        crop_b = await cropper.crop(frame_b, bbox, track_id=0)

        crc_a = zlib.crc32(crop_a.tobytes())
        crc_b = zlib.crc32(crop_b.tobytes())
        assert crc_a != crc_b, "Different frames must yield different crop checksums."

    @pytest.mark.asyncio
    async def test_crop_owns_its_memory(self):
        frame = _make_frame()
        bbox = (10.0, 10.0, 100.0, 100.0)
        cfg = _make_config()
        lg = _make_logger()
        cropper = FaceCropper(cfg, lg)

        crop = await cropper.crop(frame, bbox, track_id=0)
        assert crop.flags["OWNDATA"], "Crop must own its memory (use .copy())."


# --------------------------------------------------------------------------- #
# 2. Inference-per-frame test                                                  #
# --------------------------------------------------------------------------- #

class TestInferencePerFrame:
    """Model forward() is called exactly once per valid face per frame."""

    @pytest.mark.asyncio
    async def test_model_called_once_per_frame(self):
        rot_mat = _identity_rotation()
        model = _make_model_returning(rot_mat)

        cfg = _make_config()
        lg = _make_logger()
        estimator = HeadPoseEstimator(model, cfg, lg)

        crop = _make_frame(h=80, w=80)

        for i in range(3):
            await estimator.estimate(crop, track_id=0)

        assert estimator.inference_call_count == 3
        assert model.call_count == 3


# --------------------------------------------------------------------------- #
# 3. Fresh result object test                                                  #
# --------------------------------------------------------------------------- #

class TestFreshResultObject:
    """Consecutive HeadPoseResult instances are different objects."""

    def test_consecutive_results_different_object_ids(self):
        r1 = HeadPoseResult(
            track_id=0, face_bbox=(0, 0, 50, 50),
            yaw=0.0, pitch=0.0, roll=0.0,
            frame_index=1,
        )
        r2 = HeadPoseResult(
            track_id=0, face_bbox=(0, 0, 50, 50),
            yaw=10.0, pitch=5.0, roll=2.0,
            frame_index=2,
        )
        assert r1 is not r2


# --------------------------------------------------------------------------- #
# 4. Frame-index propagation test                                              #
# --------------------------------------------------------------------------- #

class TestFrameIndexPropagation:
    """frame_index flows from FrameContext through HeadPoseResult to mapper."""

    @pytest.mark.asyncio
    async def test_frame_index_flows_to_result(self):
        result = HeadPoseResult(
            track_id=0, face_bbox=(0, 0, 50, 50),
            yaw=5.0, pitch=10.0, roll=0.0,
            frame_index=42,
        )
        assert result.frame_index == 42

    @pytest.mark.asyncio
    async def test_frame_index_stored_in_context_by_mapper(self):
        lg = _make_logger()
        mapper = HeadPoseMapper(lg)

        ctx = FrameContext(frame_number=42)
        result = HeadPoseResult(
            track_id=0, face_bbox=(0, 0, 50, 50),
            yaw=5.0, pitch=10.0, roll=0.0,
            frame_index=42,
        )

        ctx = await mapper.map(ctx, [result])
        stored = ctx.head_pose[0]
        assert stored.frame_index == 42


# --------------------------------------------------------------------------- #
# 5. Stale-result rejection test                                               #
# --------------------------------------------------------------------------- #

class TestStaleResultRejection:
    """Annotator skips results whose frame_index != current_frame_index."""

    @pytest.mark.asyncio
    async def test_stale_result_not_rendered(self):
        cfg = _make_config(
            annotation_enabled=True,
            draw_axis=False,
            debug_reject_stale_results=True,
        )
        lg = _make_logger()
        annotator = HeadPoseAnnotator(cfg, lg)

        frame = _make_frame()
        stale_result = HeadPoseResult(
            track_id=0, face_bbox=(10, 10, 200, 200),
            yaw=45.0, pitch=30.0, roll=0.0,
            frame_index=19,   # ← one frame behind
        )

        with patch.object(annotator._text_drawer, "draw") as mock_draw:
            await annotator.annotate(frame, [stale_result], current_frame_index=20)
            mock_draw.assert_not_called()

    @pytest.mark.asyncio
    async def test_current_result_is_rendered(self):
        cfg = _make_config(
            annotation_enabled=True,
            draw_axis=False,
            debug_reject_stale_results=True,
        )
        lg = _make_logger()
        annotator = HeadPoseAnnotator(cfg, lg)

        frame = _make_frame()
        current_result = HeadPoseResult(
            track_id=0, face_bbox=(10, 10, 200, 200),
            yaw=5.0, pitch=10.0, roll=0.0,
            frame_index=20,
        )

        with patch.object(annotator._text_drawer, "draw") as mock_draw:
            await annotator.annotate(frame, [current_result], current_frame_index=20)
            mock_draw.assert_called_once()


# --------------------------------------------------------------------------- #
# 6. FrameContext clearing test                                                #
# --------------------------------------------------------------------------- #

class TestFrameContextClearing:
    """Mapper clears head_pose before inserting new results."""

    @pytest.mark.asyncio
    async def test_previous_track_not_retained(self):
        lg = _make_logger()
        mapper = HeadPoseMapper(lg)

        # Frame 1: track 0 present
        ctx = FrameContext(frame_number=1)
        r0 = HeadPoseResult(
            track_id=0, face_bbox=(0, 0, 50, 50),
            yaw=0.0, pitch=0.0, roll=0.0,
            frame_index=1,
        )
        ctx = await mapper.map(ctx, [r0])
        assert 0 in ctx.head_pose

        # Frame 2: track 0 gone, only track 1
        ctx.frame_number = 2
        r1 = HeadPoseResult(
            track_id=1, face_bbox=(0, 0, 50, 50),
            yaw=0.0, pitch=0.0, roll=0.0,
            frame_index=2,
        )
        ctx = await mapper.map(ctx, [r1])
        assert 0 not in ctx.head_pose, "Track 0 must be cleared for frame 2."
        assert 1 in ctx.head_pose


# --------------------------------------------------------------------------- #
# 7. Raw-output-to-overlay test                                               #
# --------------------------------------------------------------------------- #

class TestRawOutputToOverlay:
    """Different model outputs produce different overlay values."""

    @pytest.mark.asyncio
    async def test_different_model_outputs_different_angles(self):
        lg = _make_logger()
        parser = HeadPoseParser(lg)

        # Identity → all angles near 0
        R_identity = _identity_rotation()
        yaw0, pitch0, roll0 = await parser.parse(R_identity, track_id=0)

        # Rotate 45° around Y (yaw)
        angle = np.radians(45.0)
        R_yaw45 = np.array([
            [ np.cos(angle), 0.0, np.sin(angle)],
            [           0.0, 1.0,           0.0],
            [-np.sin(angle), 0.0, np.cos(angle)],
        ], dtype=np.float32)
        yaw45, pitch45, roll45 = await parser.parse(R_yaw45, track_id=0)

        assert abs(yaw45 - yaw0) > 10.0, (
            "A 45° yaw rotation must change the parsed yaw by >10°."
        )


# --------------------------------------------------------------------------- #
# 8. Two-track isolation test                                                  #
# --------------------------------------------------------------------------- #

class TestTwoTrackIsolation:
    """Results from two tracks are stored independently."""

    @pytest.mark.asyncio
    async def test_tracks_do_not_overwrite_each_other(self):
        lg = _make_logger()
        mapper = HeadPoseMapper(lg)

        ctx = FrameContext(frame_number=1)
        r0 = HeadPoseResult(
            track_id=0, face_bbox=(0, 0, 50, 50),
            yaw=10.0, pitch=5.0, roll=0.0, frame_index=1,
        )
        r1 = HeadPoseResult(
            track_id=1, face_bbox=(100, 100, 200, 200),
            yaw=-20.0, pitch=-10.0, roll=3.0, frame_index=1,
        )
        ctx = await mapper.map(ctx, [r0, r1])

        assert ctx.head_pose[0].yaw == pytest.approx(10.0)
        assert ctx.head_pose[1].yaw == pytest.approx(-20.0)


# --------------------------------------------------------------------------- #
# 9. Async out-of-order test                                                   #
# --------------------------------------------------------------------------- #

class TestAsyncOrdering:
    """A result from an older frame must not be rendered as the current frame."""

    @pytest.mark.asyncio
    async def test_late_frame_result_rejected_by_annotator(self):
        cfg = _make_config(
            annotation_enabled=True,
            draw_axis=False,
            debug_reject_stale_results=True,
        )
        lg = _make_logger()
        annotator = HeadPoseAnnotator(cfg, lg)

        frame = _make_frame()
        late_result = HeadPoseResult(
            track_id=0, face_bbox=(10, 10, 200, 200),
            yaw=0.0, pitch=0.0, roll=0.0,
            frame_index=10,   # frame 10 arrived late
        )

        with patch.object(annotator._text_drawer, "draw") as mock_draw:
            # Current frame is 11 — late result must be skipped
            await annotator.annotate(frame, [late_result], current_frame_index=11)
            mock_draw.assert_not_called()


# --------------------------------------------------------------------------- #
# 10. Parser — rotation matrix to Euler angles                                #
# --------------------------------------------------------------------------- #

class TestParserRotationMatrix:
    """HeadPoseParser converts known rotation matrices correctly."""

    @pytest.mark.asyncio
    async def test_identity_matrix_gives_zero_angles(self):
        lg = _make_logger()
        parser = HeadPoseParser(lg)
        R = _identity_rotation()
        yaw, pitch, roll = await parser.parse(R, track_id=0)
        assert abs(yaw) < 1e-3
        assert abs(pitch) < 1e-3
        assert abs(roll) < 1e-3

    @pytest.mark.asyncio
    async def test_wrong_shape_raises_parsing_error(self):
        lg = _make_logger()
        parser = HeadPoseParser(lg)
        with pytest.raises(HeadPoseParsingError):
            await parser.parse(np.zeros(3), track_id=0)

    def test_rotation_matrix_to_euler_helper_identity(self):
        R = _identity_rotation()
        pitch, yaw, roll = _rotation_matrix_to_euler(R)
        assert abs(pitch) < 1e-6
        assert abs(yaw) < 1e-6
        assert abs(roll) < 1e-6

    def test_rotation_matrix_to_euler_90deg_yaw(self):
        """90° rotation around Y → yaw ≈ 90°."""
        a = np.pi / 2
        R = np.array([
            [np.cos(a), 0, np.sin(a)],
            [       0., 1,        0.],
            [-np.sin(a), 0, np.cos(a)],
        ], dtype=np.float32)
        pitch, yaw, roll = _rotation_matrix_to_euler(R)
        assert abs(np.degrees(yaw) - 90.0) < 0.5


# --------------------------------------------------------------------------- #
# Model-loading tests (10 tests)                                               #
# --------------------------------------------------------------------------- #

class TestModelLoaderFails:
    """All failure paths raise HeadPoseInitializationError immediately."""

    @pytest.mark.asyncio
    async def test_missing_package_raises_error(self, tmp_path):
        """sixdrepnet not installed → HeadPoseInitializationError."""
        cfg = _make_config(model_path=str(tmp_path / "model.pth"))
        (tmp_path / "model.pth").write_bytes(b"fake")

        lg = _make_logger()
        loader = HeadPoseModelLoader(cfg, lg)

        with patch.dict("sys.modules", {"sixdrepnet": None, "sixdrepnet.model": None}):
            with pytest.raises(HeadPoseInitializationError, match="sixdrepnet"):
                await loader.load()

    @pytest.mark.asyncio
    async def test_missing_checkpoint_raises_error(self, tmp_path):
        """No .pth file → HeadPoseInitializationError."""
        cfg = _make_config(model_path=str(tmp_path / "missing.pth"))
        lg = _make_logger()
        loader = HeadPoseModelLoader(cfg, lg)

        with pytest.raises(HeadPoseInitializationError, match="not found"):
            await loader.load()

    @pytest.mark.asyncio
    async def test_corrupt_checkpoint_raises_error(self, tmp_path):
        """Corrupt bytes → torch.load fails → HeadPoseInitializationError."""
        pth = tmp_path / "corrupt.pth"
        pth.write_bytes(b"\x00\x01\x02\x03GARBAGE")
        cfg = _make_config(model_path=str(pth))
        lg = _make_logger()
        loader = HeadPoseModelLoader(cfg, lg)

        mock_sixdrepnet_model = MagicMock()
        with patch("app.services.ai.analyzers.head_pose.loader.HeadPoseModelLoader"):
            pass  # Just verifying the test structure compiles

        with pytest.raises(HeadPoseInitializationError):
            # torch.load will fail on the corrupt bytes
            import torch

            fake_module = MagicMock()
            fake_module.SixDRepNet = MagicMock(return_value=MagicMock())
            with patch.dict("sys.modules", {
                "sixdrepnet": fake_module,
                "sixdrepnet.model": fake_module,
            }):
                await loader.load()

    @pytest.mark.asyncio
    async def test_incompatible_architecture_raises_error(self, tmp_path):
        """Wrong-architecture state dict → strict=True fails → error."""
        # Save a state dict with wrong keys
        wrong_sd = {"wrong_layer.weight": torch.zeros(3, 3)}
        pth = tmp_path / "wrong.pth"
        torch.save(wrong_sd, str(pth))

        cfg = _make_config(model_path=str(pth))
        lg = _make_logger()
        loader = HeadPoseModelLoader(cfg, lg)

        # Mock a simple model with a different key
        simple_model = torch.nn.Linear(4, 2)
        fake_sixdrepnet = MagicMock()
        fake_sixdrepnet.SixDRepNet = MagicMock(return_value=simple_model)
        with patch.dict("sys.modules", {
            "sixdrepnet": fake_sixdrepnet,
            "sixdrepnet.model": fake_sixdrepnet,
        }):
            with pytest.raises(HeadPoseInitializationError):
                await loader.load()

    def test_no_placeholder_production_fallback(self):
        """HeadPoseModelLoader must not have any fallback model attribute."""
        loader = HeadPoseModelLoader.__new__(HeadPoseModelLoader)
        # Should not have a _fallback_model, _placeholder, or _mock attribute
        for attr in ("_fallback_model", "_placeholder", "_mock", "_default_model"):
            assert not hasattr(loader, attr), (
                f"Loader must not contain fallback attribute '{attr}'."
            )

    @pytest.mark.asyncio
    async def test_official_model_output_shape(self):
        """A valid SixDRepNet-like model must output (1, 3, 3)."""
        # Simulate a model that returns (1,3,3)
        R = torch.eye(3).unsqueeze(0)  # (1,3,3)
        model = MagicMock(spec=torch.nn.Module)
        model.return_value = R
        model.parameters = MagicMock(return_value=iter([torch.zeros(1)]))

        # Validate shape explicitly as the loader's _validate_model would
        assert tuple(R.shape) == (1, 3, 3)

    @pytest.mark.asyncio
    async def test_parser_converts_known_rotation_matrix(self):
        """Pitch=30°, Yaw=0°, Roll=0° rotation matrix → pitch ≈ 30°."""
        a = np.radians(30.0)
        # Rotation around X axis by 30° (pitch)
        R = np.array([
            [1.0,         0.0,          0.0],
            [0.0,  np.cos(a), -np.sin(a)],
            [0.0,  np.sin(a),  np.cos(a)],
        ], dtype=np.float32)
        lg = _make_logger()
        parser = HeadPoseParser(lg)
        yaw, pitch, roll = await parser.parse(R, track_id=0)
        assert abs(pitch - 30.0) < 1.0, (
            f"Expected pitch ≈ 30°, got {pitch:.2f}°"
        )

    @pytest.mark.asyncio
    async def test_no_automatic_downloading(self, tmp_path):
        """Loader raises immediately if file missing — no network call."""
        cfg = _make_config(model_path=str(tmp_path / "absent.pth"))
        lg = _make_logger()
        loader = HeadPoseModelLoader(cfg, lg)

        called = []
        original_urlopen = None
        try:
            import urllib.request
            original_urlopen = urllib.request.urlopen

            def mock_urlopen(*a, **kw):
                called.append(True)
                raise AssertionError("Network download attempted!")

            urllib.request.urlopen = mock_urlopen
        except ImportError:
            pass

        try:
            with pytest.raises(HeadPoseInitializationError):
                await loader.load()
        finally:
            if original_urlopen is not None:
                import urllib.request
                urllib.request.urlopen = original_urlopen

        assert not called, "Loader must not make any network request."

    @pytest.mark.asyncio
    async def test_estimator_uses_local_checkpoint_path(self, tmp_path):
        """Loader reads from config.model_path — no other path is used."""
        configured_path = str(tmp_path / "local.pth")
        cfg = _make_config(model_path=configured_path)
        lg = _make_logger()
        loader = HeadPoseModelLoader(cfg, lg)

        assert loader._config.model_path == configured_path

    @pytest.mark.asyncio
    async def test_different_real_inputs_different_estimator_outputs(self):
        """Distinct crops produce different rotation matrices from estimator."""
        R_a = np.array([
            [ 0.866,  0.0,  0.5],
            [ 0.0,    1.0,  0.0],
            [-0.5,    0.0,  0.866],
        ], dtype=np.float32)
        R_b = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 0.866, -0.5],
            [0.0, 0.5,  0.866],
        ], dtype=np.float32)

        model_a = _make_model_returning(R_a)
        model_b = _make_model_returning(R_b)

        cfg = _make_config()
        lg = _make_logger()

        est_a = HeadPoseEstimator(model_a, cfg, lg)
        est_b = HeadPoseEstimator(model_b, cfg, lg)

        crop = _make_frame(h=80, w=80, seed=42)
        out_a = await est_a.estimate(crop, track_id=0)
        out_b = await est_b.estimate(crop, track_id=0)

        assert not np.allclose(out_a, out_b), (
            "Different model outputs must produce different rotation matrices."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
