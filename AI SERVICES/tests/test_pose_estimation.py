"""Unit tests for YOLO pose estimation."""

import asyncio
import sys
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(__file__).split("tests")[0])

from app.services.ai.analyzers.pose.associator import PoseAssociator
from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.iou_calculator import IoUCalculator
from app.services.ai.analyzers.pose.mapper import PoseMapper
from app.services.ai.analyzers.pose.pose import PoseResult
from app.services.ai.analyzers.pose.validator import PoseValidator
from app.services.ai.pipeline.context import FrameContext, Detection
from app.services.ai.trackers.deepsort.track import Track


class TestPoseValidator:
    """Tests for PoseValidator."""
    
    def test_valid_pose_candidate(self):
        """Test validation of valid pose candidate."""
        config = YoloPoseConfig()
        validator = PoseValidator(config)
        
        candidate = {
            'bbox': [100, 100, 200, 300],
            'keypoints': [[150, 150]] * 17,
            'keypoint_confidences': [0.8] * 17,
            'confidence': 0.9,
        }
        
        valid = validator.validate([candidate], 640, 480)
        assert len(valid) == 1
    
    def test_invalid_bbox_rejected(self):
        """Test invalid bounding box is rejected."""
        config = YoloPoseConfig()
        validator = PoseValidator(config)
        
        # Invalid: x2 <= x1
        candidate = {
            'bbox': [200, 100, 100, 300],
            'keypoints': [[150, 150]] * 17,
            'keypoint_confidences': [0.8] * 17,
            'confidence': 0.9,
        }
        
        valid = validator.validate([candidate], 640, 480)
        assert len(valid) == 0
    
    def test_low_confidence_rejected(self):
        """Test low confidence pose is rejected."""
        config = YoloPoseConfig()
        validator = PoseValidator(config)
        
        candidate = {
            'bbox': [100, 100, 200, 300],
            'keypoints': [[150, 150]] * 17,
            'keypoint_confidences': [0.8] * 17,
            'confidence': 0.1,  # Below threshold
        }
        
        valid = validator.validate([candidate], 640, 480)
        assert len(valid) == 0
    
    def test_too_few_visible_keypoints_rejected(self):
        """Test pose with too few visible keypoints is rejected."""
        config = YoloPoseConfig()
        validator = PoseValidator(config)
        
        # Only 3 visible keypoints (below threshold of 5)
        confidences = [0.8] * 3 + [0.1] * 14
        candidate = {
            'bbox': [100, 100, 200, 300],
            'keypoints': [[150, 150]] * 17,
            'keypoint_confidences': confidences,
            'confidence': 0.9,
        }
        
        valid = validator.validate([candidate], 640, 480)
        assert len(valid) == 0


class TestPoseAssociator:
    """Tests for PoseAssociator."""
    
    def test_single_pose_single_track_match(self):
        """Test single pose matches single track with high IoU."""
        config = YoloPoseConfig(track_iou_threshold=0.3)
        associator = PoseAssociator(config)
        
        track = Track(
            track_id=0,
            bbox=(100, 100, 200, 300),
            center=(150, 200),
            confidence=0.9,
            is_confirmed=True,
            age=5,
            hits=5,
            time_since_update=0,
            class_name="person",
        )
        
        pose_candidate = {
            'bbox': [105, 105, 195, 295],  # High IoU with track
            'keypoints': [[150, 150]] * 17,
            'keypoint_confidences': [0.8] * 17,
            'confidence': 0.9,
        }
        
        results = associator.associate([track], [pose_candidate])
        assert len(results) == 1
        assert results[0].track_id == 0
    
    def test_low_iou_no_match(self):
        """Test low IoU results in no match."""
        config = YoloPoseConfig(track_iou_threshold=0.5)
        associator = PoseAssociator(config)
        
        track = Track(
            track_id=0,
            bbox=(100, 100, 200, 300),
            center=(150, 200),
            confidence=0.9,
            is_confirmed=True,
            age=5,
            hits=5,
            time_since_update=0,
            class_name="person",
        )
        
        pose_candidate = {
            'bbox': [400, 400, 500, 600],  # Low IoU with track
            'keypoints': [[450, 500]] * 17,
            'keypoint_confidences': [0.8] * 17,
            'confidence': 0.9,
        }
        
        results = associator.associate([track], [pose_candidate])
        assert len(results) == 0
    
    def test_one_to_one_matching(self):
        """Test one-to-one matching prevents multiple assignments."""
        config = YoloPoseConfig(track_iou_threshold=0.3)
        associator = PoseAssociator(config)
        
        track1 = Track(
            track_id=0,
            bbox=(100, 100, 200, 300),
            center=(150, 200),
            confidence=0.9,
            is_confirmed=True,
            age=5,
            hits=5,
            time_since_update=0,
            class_name="person",
        )
        
        track2 = Track(
            track_id=1,
            bbox=(300, 100, 400, 300),
            center=(350, 200),
            confidence=0.9,
            is_confirmed=True,
            age=5,
            hits=5,
            time_since_update=0,
            class_name="person",
        )
        
        pose1 = {
            'bbox': [105, 105, 195, 295],  # Matches track1
            'keypoints': [[150, 150]] * 17,
            'keypoint_confidences': [0.8] * 17,
            'confidence': 0.9,
        }
        
        pose2 = {
            'bbox': [305, 105, 395, 295],  # Matches track2
            'keypoints': [[350, 150]] * 17,
            'keypoint_confidences': [0.8] * 17,
            'confidence': 0.9,
        }
        
        results = associator.associate([track1, track2], [pose1, pose2])
        assert len(results) == 2
        assert results[0].track_id == 0
        assert results[1].track_id == 1


class TestPoseMapper:
    """Tests for PoseMapper."""
    
    def test_map_poses_to_context(self):
        """Test mapping poses to FrameContext."""
        mapper = PoseMapper()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        context = FrameContext(frame=frame, frame_number=1, timestamp=datetime.now())
        
        poses = [
            PoseResult(
                track_id=0,
                bbox=(100, 100, 200, 300),
                keypoints=[(150, 150)] * 17,
                keypoint_confidences=[0.8] * 17,
                confidence=0.9,
                is_valid=True,
                visible_keypoints=17,
            ),
            PoseResult(
                track_id=1,
                bbox=(300, 100, 400, 300),
                keypoints=[(350, 150)] * 17,
                keypoint_confidences=[0.8] * 17,
                confidence=0.9,
                is_valid=True,
                visible_keypoints=17,
            ),
        ]
        
        context = mapper.map(context, poses)
        
        assert len(context.poses) == 2
        assert 0 in context.poses
        assert 1 in context.poses
        assert context.poses[0].track_id == 0
        assert context.poses[1].track_id == 1


class TestIoUCalculation:
    """Tests for IoU calculation."""
    
    def test_iou_identical_boxes(self):
        """Test IoU of identical boxes is 1.0."""
        iou_calc = IoUCalculator()
        
        bbox1 = (100, 100, 200, 300)
        bbox2 = [100, 100, 200, 300]
        
        iou = iou_calc.calculate_iou(bbox1, bbox2)
        assert iou == 1.0
    
    def test_iou_no_overlap(self):
        """Test IoU of non-overlapping boxes is 0.0."""
        iou_calc = IoUCalculator()
        
        bbox1 = (100, 100, 200, 300)
        bbox2 = [400, 400, 500, 600]
        
        iou = iou_calc.calculate_iou(bbox1, bbox2)
        assert iou == 0.0
    
    def test_iou_partial_overlap(self):
        """Test IoU of partially overlapping boxes."""
        iou_calc = IoUCalculator()
        
        bbox1 = (100, 100, 200, 300)  # Area: 100 * 200 = 20000
        bbox2 = [150, 150, 250, 350]  # Area: 100 * 200 = 20000
        # Intersection: 50 * 150 = 7500
        # Union: 20000 + 20000 - 7500 = 32500
        # IoU: 7500 / 32500 ≈ 0.231
        
        iou = iou_calc.calculate_iou(bbox1, bbox2)
        assert 0.23 < iou < 0.24


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
