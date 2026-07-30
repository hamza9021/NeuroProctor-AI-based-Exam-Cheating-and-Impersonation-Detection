"""Head pose quality evaluator for frame reliability assessment."""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass
class HeadPoseQuality:
    """Quality assessment for a head pose result.

    Attributes:
        score: Overall quality score (0.0 to 1.0).
        is_valid_for_smoothing: Whether this frame should be used for temporal smoothing.
        is_valid_for_rules: Whether this frame should be used for cheating rule evaluation.
        reason: Human-readable reason for quality decision.
    """
    score: float
    is_valid_for_smoothing: bool
    is_valid_for_rules: bool
    reason: Optional[str] = None


class HeadPoseQualityEvaluator:
    """Evaluates head pose frame quality using lightweight metrics."""

    def __init__(
        self,
        min_visible_keypoints: int = 2,
        min_nose_confidence: float = 0.5,
        min_crop_size: int = 60,
        max_crop_size: int = 400,
        min_aspect_ratio: float = 0.5,
        max_aspect_ratio: float = 2.0,
        min_smoothing_score: float = 0.4,
        min_rules_score: float = 0.7,
    ):
        """Initialize quality evaluator.

        Args:
            min_visible_keypoints: Minimum visible facial keypoints (nose, eyes, ears).
            min_nose_confidence: Minimum nose keypoint confidence.
            min_crop_size: Minimum crop size in pixels.
            max_crop_size: Maximum crop size in pixels.
            min_aspect_ratio: Minimum crop aspect ratio (width/height).
            max_aspect_ratio: Maximum crop aspect ratio (width/height).
            min_smoothing_score: Minimum score for temporal smoothing.
            min_rules_score: Minimum score for cheating rule evaluation.
        """
        self._min_visible_keypoints = min_visible_keypoints
        self._min_nose_confidence = min_nose_confidence
        self._min_crop_size = min_crop_size
        self._max_crop_size = max_crop_size
        self._min_aspect_ratio = min_aspect_ratio
        self._max_aspect_ratio = max_aspect_ratio
        self._min_smoothing_score = min_smoothing_score
        self._min_rules_score = min_rules_score

    def evaluate(
        self,
        visible_facial_keypoints: int,
        nose_confidence: float,
        crop_shape: Tuple[int, int, int],
        crop_bbox: Tuple[float, float, float, float],
        rotation_matrix: Optional[np.ndarray] = None,
    ) -> HeadPoseQuality:
        """Evaluate head pose frame quality.

        Args:
            visible_facial_keypoints: Count of visible facial keypoints (nose, eyes, ears).
            nose_confidence: Nose keypoint confidence score.
            crop_shape: Face crop shape (height, width, channels).
            crop_bbox: Face crop bounding box (x1, y1, x2, y2).
            rotation_matrix: SixDRepNet rotation matrix (3, 3), if available.

        Returns:
            HeadPoseQuality assessment.
        """
        score = 0.0
        reasons = []

        # 1. Visible facial keypoints (weight: 0.3)
        keypoint_score = min(visible_facial_keypoints / 5.0, 1.0)  # Max 5 keypoints
        if visible_facial_keypoints >= self._min_visible_keypoints:
            score += keypoint_score * 0.3
        else:
            reasons.append(f"insufficient_keypoints({visible_facial_keypoints})")

        # 2. Nose confidence (weight: 0.2)
        if nose_confidence >= self._min_nose_confidence:
            score += nose_confidence * 0.2
        else:
            reasons.append(f"low_nose_confidence({nose_confidence:.2f})")

        # 3. Crop size (weight: 0.2)
        crop_h, crop_w = crop_shape[:2]
        crop_size = max(crop_h, crop_w)
        if self._min_crop_size <= crop_size <= self._max_crop_size:
            size_score = 1.0 - abs(crop_size - 150) / 150.0  # Ideal ~150px
            size_score = max(0.0, size_score)
            score += size_score * 0.2
        else:
            reasons.append(f"invalid_crop_size({crop_size}px)")

        # 4. Crop aspect ratio (weight: 0.15)
        aspect_ratio = crop_w / crop_h if crop_h > 0 else 0.0
        if self._min_aspect_ratio <= aspect_ratio <= self._max_aspect_ratio:
            # Prefer square crops (aspect ratio ~1.0)
            ar_score = 1.0 - abs(aspect_ratio - 1.0)
            ar_score = max(0.0, ar_score)
            score += ar_score * 0.15
        else:
            reasons.append(f"invalid_aspect_ratio({aspect_ratio:.2f})")

        # 5. Finite model output (weight: 0.15)
        if rotation_matrix is not None and np.isfinite(rotation_matrix).all():
            score += 0.15
        else:
            reasons.append("invalid_rotation_matrix")

        # Clamp score to [0, 1]
        score = max(0.0, min(1.0, score))

        # Determine validity thresholds
        is_valid_for_smoothing = score >= self._min_smoothing_score
        is_valid_for_rules = score >= self._min_rules_score

        reason = "; ".join(reasons) if reasons else None

        return HeadPoseQuality(
            score=score,
            is_valid_for_smoothing=is_valid_for_smoothing,
            is_valid_for_rules=is_valid_for_rules,
            reason=reason,
        )
