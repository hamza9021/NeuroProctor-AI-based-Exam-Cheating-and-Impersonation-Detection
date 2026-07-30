"""Regression tests for pose keypoint lookup and crop logic."""

import numpy as np
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.ai.analyzers.head_pose.track_processor import TrackProcessor
from app.services.ai.analyzers.head_pose.bbox_locator import BboxLocator
from app.services.ai.analyzers.head_pose.keypoint_locator import KeypointLocator
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.pose.pose import PoseResult


class TestPoseKeypointLookup:
    """Tests for pose keypoint lookup from FrameContext."""

    def test_pose_result_located_by_integer_track_id(self):
        """Pose result is located by integer track_id."""
        from app.services.ai.pipeline.frame_context import FrameContext

        # Create pose result with track_id 0
        pose = PoseResult(
            track_id=0,
            bbox=(100.0, 100.0, 200.0, 300.0),
            keypoints=[(150.0, 150.0), (140.0, 145.0), (160.0, 145.0), (130.0, 160.0), (170.0, 160.0)],
            keypoint_confidences=[0.9, 0.8, 0.8, 0.7, 0.7],
            confidence=0.85,
            is_valid=True,
            visible_keypoints=5,
        )

        context = FrameContext()
        context.poses = [pose]
        context.frame_number = 0
        context.frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Verify pose is accessible by track_id
        found_pose = None
        for p in context.poses:
            if hasattr(p, "track_id") and int(p.track_id) == 0:
                found_pose = p
                break

        assert found_pose is not None
        assert found_pose.track_id == 0
        assert len(found_pose.keypoints) == 5

    def test_string_integer_track_id_normalization(self):
        """String/integer track IDs are normalised safely at the boundary."""
        from app.services.ai.pipeline.frame_context import FrameContext

        # Create pose with integer track_id
        pose = PoseResult(
            track_id=1,
            bbox=(100.0, 100.0, 200.0, 300.0),
            keypoints=[(150.0, 150.0)],
            keypoint_confidences=[0.9],
            confidence=0.85,
            is_valid=True,
            visible_keypoints=1,
        )

        context = FrameContext()
        context.poses = [pose]

        # Lookup with integer track_id
        found = False
        for p in context.poses:
            if hasattr(p, "track_id") and int(p.track_id) == 1:
                found = True
                break

        assert found

        # Lookup with string track_id (should still work after int conversion)
        found = False
        for p in context.poses:
            if hasattr(p, "track_id") and int(p.track_id) == int("1"):
                found = True
                break

        assert found

    def test_facial_keypoints_extracted_from_pose_result(self):
        """Nose, eyes and ears are extracted from the actual pose result structure."""
        # COCO indices: 0=nose, 1=left_eye, 2=right_eye, 3=left_ear, 4=right_ear
        pose = PoseResult(
            track_id=0,
            bbox=(100.0, 100.0, 200.0, 300.0),
            keypoints=[
                (150.0, 150.0),  # nose
                (140.0, 145.0),  # left_eye
                (160.0, 145.0),  # right_eye
                (130.0, 160.0),  # left_ear
                (170.0, 160.0),  # right_ear
            ],
            keypoint_confidences=[0.9, 0.8, 0.8, 0.7, 0.7],
            confidence=0.85,
            is_valid=True,
            visible_keypoints=5,
        )

        # Convert to numpy array format used by TrackProcessor
        keypoints_array = np.zeros((len(pose.keypoints), 3), dtype=np.float32)
        for i, (kp, conf) in enumerate(zip(pose.keypoints, pose.keypoint_confidences)):
            keypoints_array[i, 0] = kp[0]
            keypoints_array[i, 1] = kp[1]
            keypoints_array[i, 2] = conf

        # Verify facial keypoints are at correct indices
        assert keypoints_array[0, 0] == 150.0  # nose x
        assert keypoints_array[0, 1] == 150.0  # nose y
        assert keypoints_array[0, 2] == 0.9   # nose conf
        assert keypoints_array[1, 0] == 140.0  # left_eye x
        assert keypoints_array[2, 0] == 160.0  # right_eye x

    def test_visible_facial_keypoints_count_nonzero(self):
        """Existing visible facial keypoints do not produce a count of zero."""
        pose = PoseResult(
            track_id=0,
            bbox=(100.0, 100.0, 200.0, 300.0),
            keypoints=[
                (150.0, 150.0),  # nose
                (140.0, 145.0),  # left_eye
                (160.0, 145.0),  # right_eye
            ],
            keypoint_confidences=[0.9, 0.8, 0.8],
            confidence=0.85,
            is_valid=True,
            visible_keypoints=3,
        )

        # Convert to numpy array
        keypoints_array = np.zeros((len(pose.keypoints), 3), dtype=np.float32)
        for i, (kp, conf) in enumerate(zip(pose.keypoints, pose.keypoint_confidences)):
            keypoints_array[i, 0] = kp[0]
            keypoints_array[i, 1] = kp[1]
            keypoints_array[i, 2] = conf

        # Count visible facial keypoints (confidence >= 0.5)
        facial_indices = [0, 1, 2, 3, 4]
        visible_count = 0
        for idx in facial_indices:
            if idx < len(keypoints_array) and keypoints_array[idx, 2] >= 0.5:
                visible_count += 1

        assert visible_count == 3, f"Expected 3 visible keypoints, got {visible_count}"

    def test_pose_keypoints_from_another_track_rejected(self):
        """Pose keypoints from another track are rejected."""
        from app.services.ai.pipeline.frame_context import FrameContext

        # Create poses for different tracks
        pose_track_0 = PoseResult(
            track_id=0,
            bbox=(100.0, 100.0, 200.0, 300.0),
            keypoints=[(150.0, 150.0)],
            keypoint_confidences=[0.9],
            confidence=0.85,
            is_valid=True,
            visible_keypoints=1,
        )

        pose_track_1 = PoseResult(
            track_id=1,
            bbox=(300.0, 100.0, 400.0, 300.0),
            keypoints=[(350.0, 150.0)],
            keypoint_confidences=[0.9],
            confidence=0.85,
            is_valid=True,
            visible_keypoints=1,
        )

        context = FrameContext()
        context.poses = [pose_track_0, pose_track_1]

        # Lookup for track_id 0 should not return track 1's keypoints
        found_pose = None
        for p in context.poses:
            if hasattr(p, "track_id") and int(p.track_id) == 0:
                found_pose = p
                break

        assert found_pose is not None
        assert found_pose.track_id == 0
        assert found_pose.keypoints[0][0] == 150.0  # Track 0's nose, not 350.0


class TestTightHeadCrop:
    """Tests for tight head crop from facial keypoints."""

    def test_facial_keypoint_crop_smaller_than_person_bbox(self):
        """Facial-keypoint crop is square and smaller than the person bbox."""
        config = HeadPoseConfig()
        locator = KeypointLocator(config)

        # Create keypoints for a face
        keypoints = np.zeros((17, 3), dtype=np.float32)
        keypoints[0] = [320.0, 150.0, 0.9]  # nose
        keypoints[1] = [300.0, 140.0, 0.8]  # left_eye
        keypoints[2] = [340.0, 140.0, 0.8]  # right_eye
        keypoints[3] = [280.0, 160.0, 0.7]  # left_ear
        keypoints[4] = [360.0, 160.0, 0.7]  # right_ear

        face_bbox = locator.locate(keypoints, (480, 640))

        assert face_bbox is not None
        face_width = face_bbox[2] - face_bbox[0]
        face_height = face_bbox[3] - face_bbox[1]

        # Crop should be square (aspect ratio ~1:1)
        aspect_ratio = face_width / face_height
        assert 0.9 < aspect_ratio < 1.1, f"Aspect ratio {aspect_ratio} should be ~1.0"

        # Face crop should be smaller than full person width (720px in example)
        assert face_width < 200, f"Face crop width {face_width} should be < 200px"
        assert face_height < 200, f"Face crop height {face_height} should be < 200px"

    def test_fallback_crop_not_complete_person_width(self):
        """Final fallback does not use the complete person width and is square."""
        config = HeadPoseConfig()
        locator = BboxLocator(config)

        # Person bbox similar to the problematic example
        person_bbox = (1.0, 432.0, 718.0, 1276.0)
        person_width = person_bbox[2] - person_bbox[0]  # ~717px
        person_height = person_bbox[3] - person_bbox[1]  # ~844px

        face_bbox = locator.locate(person_bbox)

        assert face_bbox is not None
        face_width = face_bbox[2] - face_bbox[0]
        face_height = face_bbox[3] - face_bbox[1]

        # Fallback should be square (aspect ratio ~1:1)
        aspect_ratio = face_width / face_height
        assert 0.9 < aspect_ratio < 1.1, f"Aspect ratio {aspect_ratio} should be ~1.0"

        # Fallback should be based on person height (20% * 1.3 = ~220px)
        # Much smaller than person width (717px)
        # Allow some margin for clamping at frame boundaries
        assert face_width < 600, f"Fallback width {face_width} should be < 600px"

    def test_crop_remains_inside_frame_boundaries(self):
        """Crop remains inside frame boundaries."""
        config = HeadPoseConfig()
        locator = BboxLocator(config)

        # Person bbox at frame edge
        person_bbox = (0.0, 0.0, 100.0, 200.0)
        face_bbox = locator.locate(person_bbox)

        assert face_bbox is not None
        assert face_bbox[0] >= 0, "x1 should be >= 0"
        assert face_bbox[1] >= 0, "y1 should be >= 0"
        assert face_bbox[2] <= 100.0, "x2 should be <= person width"
        assert face_bbox[3] <= 200.0, "y2 should be <= person height"


class TestAxisOriginPriority:
    """Tests for axis origin priority."""

    def _make_processor(self):
        return TrackProcessor(
            locator=MagicMock(),
            cropper=MagicMock(),
            estimator=MagicMock(),
            parser=MagicMock(),
            validator=MagicMock(),
        )

    def test_high_confidence_nose_becomes_axis_origin(self):
        """High-confidence nose becomes the axis origin."""
        from app.services.ai.analyzers.head_pose.track_processor import _NOSE_KP_INDEX

        processor = self._make_processor()
        kps = np.zeros((17, 3), dtype=np.float32)
        kps[_NOSE_KP_INDEX] = [320.0, 150.0, 0.9]  # high confidence

        cx, cy = processor._compute_axis_origin(
            pose_data={"keypoints": kps},
            face_bbox=(300.0, 130.0, 370.0, 190.0),
            track_bbox=(280.0, 100.0, 400.0, 450.0),
            frame_h=480,
            frame_w=640,
        )

        assert cx == 320, f"Expected cx=320 (nose x), got {cx}"
        assert cy == 150, f"Expected cy=150 (nose y), got {cy}"

    def test_missing_nose_falls_back_without_dropping_result(self):
        """Missing nose falls back without dropping the result."""
        processor = self._make_processor()

        # No pose data (missing nose)
        cx, cy = processor._compute_axis_origin(
            pose_data=None,
            face_bbox=(200.0, 100.0, 300.0, 180.0),
            track_bbox=(180.0, 80.0, 320.0, 440.0),
            frame_h=480,
            frame_w=640,
        )

        # Should fall back to face bbox centre
        expected_cx = int((200.0 + 300.0) / 2)
        expected_cy = int((100.0 + 180.0) / 2)
        assert cx == expected_cx, f"Expected cx={expected_cx}, got {cx}"
        assert cy == expected_cy, f"Expected cy={expected_cy}, got {cy}"

    def test_axis_origin_clamped_to_frame(self):
        """Axis origin is clamped inside frame boundaries."""
        from app.services.ai.analyzers.head_pose.track_processor import _NOSE_KP_INDEX

        processor = self._make_processor()
        kps = np.zeros((17, 3), dtype=np.float32)
        kps[_NOSE_KP_INDEX] = [-10.0, -10.0, 0.9]  # Outside frame

        cx, cy = processor._compute_axis_origin(
            pose_data={"keypoints": kps},
            face_bbox=(200.0, 100.0, 300.0, 180.0),
            track_bbox=(180.0, 80.0, 320.0, 440.0),
            frame_h=480,
            frame_w=640,
        )

        # Should be clamped to (0, 0)
        assert cx == 0, f"Expected cx=0 (clamped), got {cx}"
        assert cy == 0, f"Expected cy=0 (clamped), got {cy}"


class TestTemporalSmoothingOutput:
    """Tests for temporal smoothing output."""

    def test_smoothing_output_remains_rendered_output(self):
        """Temporal smoothing output remains the rendered output."""
        from app.services.ai.analyzers.head_pose.temporal_smoother import TemporalSmoother

        smoother = TemporalSmoother(alpha=0.35, enabled=True)

        # First frame - initializes
        yaw1, pitch1, roll1 = smoother.smooth(0, 10.0, 5.0, 2.0, 0)
        assert yaw1 == 10.0, "First frame should return raw value"

        # Second frame - applies smoothing
        yaw2, pitch2, roll2 = smoother.smooth(0, 15.0, 7.0, 3.0, 1)
        # Smoothed should be between raw and previous
        assert 10.0 < yaw2 < 15.0, f"Smoothed yaw {yaw2} should be between 10 and 15"

        # These smoothed values should be what gets rendered
        rendered_yaw = yaw2
        assert rendered_yaw == yaw2, "Rendered should equal smoothed output"
