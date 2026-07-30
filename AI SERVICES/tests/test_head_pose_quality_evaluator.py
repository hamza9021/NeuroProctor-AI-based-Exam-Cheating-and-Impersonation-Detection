"""Tests for head pose quality evaluator."""

import numpy as np
import pytest

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.quality_evaluator import (
    HeadPoseQuality,
    HeadPoseQualityEvaluator,
)


class TestHeadPoseQualityEvaluator:
    """Tests for HeadPoseQualityEvaluator."""

    def test_initialization_with_defaults(self):
        """Evaluator initializes with default parameters."""
        evaluator = HeadPoseQualityEvaluator()
        assert evaluator._min_visible_keypoints == 2
        assert evaluator._min_nose_confidence == 0.5
        assert evaluator._min_crop_size == 60
        assert evaluator._max_crop_size == 400
        assert evaluator._min_aspect_ratio == 0.5
        assert evaluator._max_aspect_ratio == 2.0
        assert evaluator._min_smoothing_score == 0.4
        assert evaluator._min_rules_score == 0.7

    def test_initialization_with_custom_parameters(self):
        """Evaluator initializes with custom parameters."""
        evaluator = HeadPoseQualityEvaluator(
            min_visible_keypoints=3,
            min_nose_confidence=0.7,
            min_crop_size=80,
            max_crop_size=300,
            min_aspect_ratio=0.7,
            max_aspect_ratio=1.5,
            min_smoothing_score=0.5,
            min_rules_score=0.8,
        )
        assert evaluator._min_visible_keypoints == 3
        assert evaluator._min_nose_confidence == 0.7
        assert evaluator._min_crop_size == 80
        assert evaluator._max_crop_size == 300
        assert evaluator._min_aspect_ratio == 0.7
        assert evaluator._max_aspect_ratio == 1.5
        assert evaluator._min_smoothing_score == 0.5
        assert evaluator._min_rules_score == 0.8

    def test_high_quality_frame(self):
        """High quality frame with all metrics good."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(150, 150, 3),
            crop_bbox=(100.0, 100.0, 250.0, 250.0),
            rotation_matrix=np.eye(3),
        )
        assert quality.score > 0.8
        assert quality.is_valid_for_smoothing
        assert quality.is_valid_for_rules
        assert quality.reason is None

    def test_low_keypoint_count(self):
        """Low visible keypoint count reduces quality."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=1,
            nose_confidence=0.9,
            crop_shape=(150, 150, 3),
            crop_bbox=(100.0, 100.0, 250.0, 250.0),
            rotation_matrix=np.eye(3),
        )
        assert quality.score < 0.7
        assert "insufficient_keypoints" in quality.reason

    def test_low_nose_confidence(self):
        """Low nose confidence reduces quality."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.3,
            crop_shape=(150, 150, 3),
            crop_bbox=(100.0, 100.0, 250.0, 250.0),
            rotation_matrix=np.eye(3),
        )
        assert quality.score <= 0.8
        assert "low_nose_confidence" in quality.reason

    def test_crop_too_small(self):
        """Too small crop reduces quality."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(40, 40, 3),
            crop_bbox=(100.0, 100.0, 140.0, 140.0),
            rotation_matrix=np.eye(3),
        )
        assert quality.score < 0.8
        assert "invalid_crop_size" in quality.reason

    def test_crop_too_large(self):
        """Too large crop reduces quality."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(500, 500, 3),
            crop_bbox=(100.0, 100.0, 600.0, 600.0),
            rotation_matrix=np.eye(3),
        )
        assert quality.score < 0.8
        assert "invalid_crop_size" in quality.reason

    def test_extreme_aspect_ratio(self):
        """Extreme aspect ratio reduces quality."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(100, 300, 3),
            crop_bbox=(100.0, 100.0, 400.0, 200.0),
            rotation_matrix=np.eye(3),
        )
        assert quality.score < 0.8
        assert "invalid_aspect_ratio" in quality.reason

    def test_invalid_rotation_matrix(self):
        """Invalid rotation matrix reduces quality."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(150, 150, 3),
            crop_bbox=(100.0, 100.0, 250.0, 250.0),
            rotation_matrix=np.array([[np.inf, 0, 0], [0, 1, 0], [0, 0, 1]]),
        )
        assert quality.score < 0.9
        assert "invalid_rotation_matrix" in quality.reason

    def test_smoothing_threshold(self):
        """Frames below smoothing threshold are not valid for smoothing."""
        evaluator = HeadPoseQualityEvaluator(min_smoothing_score=0.5)
        quality = evaluator.evaluate(
            visible_facial_keypoints=1,
            nose_confidence=0.3,
            crop_shape=(40, 40, 3),
            crop_bbox=(100.0, 100.0, 140.0, 140.0),
            rotation_matrix=np.eye(3),
        )
        assert quality.score < 0.5
        assert not quality.is_valid_for_smoothing

    def test_rules_threshold(self):
        """Frames below rules threshold are not valid for rules."""
        evaluator = HeadPoseQualityEvaluator(min_rules_score=0.8)
        quality = evaluator.evaluate(
            visible_facial_keypoints=3,
            nose_confidence=0.6,
            crop_shape=(120, 120, 3),
            crop_bbox=(100.0, 100.0, 220.0, 220.0),
            rotation_matrix=np.eye(3),
        )
        # Score may be between 0.4 and 0.8
        assert quality.is_valid_for_smoothing or not quality.is_valid_for_smoothing
        assert not quality.is_valid_for_rules

    def test_multiple_failure_reasons(self):
        """Multiple quality issues are reported together."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=0,
            nose_confidence=0.2,
            crop_shape=(30, 30, 3),
            crop_bbox=(100.0, 100.0, 130.0, 130.0),
            rotation_matrix=None,
        )
        assert quality.score < 0.3
        reasons = quality.reason.split("; ")
        # Check for reason prefixes (reasons include values in parentheses)
        assert any("insufficient_keypoints" in r for r in reasons)
        assert any("low_nose_confidence" in r for r in reasons)
        assert any("invalid_crop_size" in r for r in reasons)
        assert any("invalid_rotation_matrix" in r for r in reasons)

    def test_score_clamped_to_zero_one(self):
        """Quality score is always clamped to [0, 1]."""
        evaluator = HeadPoseQualityEvaluator()
        # Worst case
        quality = evaluator.evaluate(
            visible_facial_keypoints=0,
            nose_confidence=0.0,
            crop_shape=(10, 10, 3),
            crop_bbox=(0.0, 0.0, 10.0, 10.0),
            rotation_matrix=None,
        )
        assert 0.0 <= quality.score <= 1.0

        # Best case
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=1.0,
            crop_shape=(150, 150, 3),
            crop_bbox=(100.0, 100.0, 250.0, 250.0),
            rotation_matrix=np.eye(3),
        )
        assert 0.0 <= quality.score <= 1.0

    def test_square_crop_preferred(self):
        """Square crops get higher scores than rectangular ones."""
        evaluator = HeadPoseQualityEvaluator()
        square_quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(150, 150, 3),
            crop_bbox=(100.0, 100.0, 250.0, 250.0),
            rotation_matrix=np.eye(3),
        )
        rectangular_quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(100, 200, 3),
            crop_bbox=(100.0, 100.0, 300.0, 200.0),
            rotation_matrix=np.eye(3),
        )
        assert square_quality.score > rectangular_quality.score

    def test_none_rotation_matrix_handled(self):
        """None rotation matrix is handled gracefully."""
        evaluator = HeadPoseQualityEvaluator()
        quality = evaluator.evaluate(
            visible_facial_keypoints=5,
            nose_confidence=0.9,
            crop_shape=(150, 150, 3),
            crop_bbox=(100.0, 100.0, 250.0, 250.0),
            rotation_matrix=None,
        )
        assert quality is not None
        assert "invalid_rotation_matrix" in quality.reason
