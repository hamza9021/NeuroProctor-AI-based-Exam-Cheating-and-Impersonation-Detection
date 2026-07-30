"""Tests for phone detection functionality."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from unittest.mock import Mock, MagicMock
import numpy as np

from app.services.ai.detectors.phone.config import PhoneDetectionConfig
from app.services.ai.detectors.phone.temporal_tracker import PhoneTemporalTracker, PhoneTrack, PhoneState
from app.services.ai.detectors.phone.service import PhoneDetectionService
from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.common.device_resolver import resolve_device
from app.services.ai.analyzers.phone.associator import PhoneStudentAssociator, AssociationResult
from app.config.settings import Settings


class TestPhoneDetectionConfig:
    """Test phone detection configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PhoneDetectionConfig()
        assert config.enabled is True
        assert config.model_path == ""
        assert config.class_name == "cell phone"
        assert config.confidence == 0.10
        assert config.image_size == 960
        assert config.fallback_image_sizes == [768, 640]
        assert config.min_box_area == 10
        assert config.roi_enabled is True
        assert config.roi_expansion == 0.15
        assert config.temporal_confirm_frames == 3
        assert config.temporal_max_missed_frames == 2
        assert config.association_iou == 0.10
        assert config.deduplication_iou == 0.50
        assert config.raw_debug_confidence == 0.01
        assert config.raw_debug_image_size == 1280
        assert config.test_max_frames == 0
        assert config.test_start_frame == 0
        assert config.test_end_frame == 0
        assert config.test_frame_step == 1
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = PhoneDetectionConfig(
            enabled=False,
            confidence=0.15,
            image_size=1280,
            temporal_confirm_frames=5,
            test_max_frames=100,
        )
        assert config.enabled is False
        assert config.confidence == 0.15
        assert config.image_size == 1280
        assert config.temporal_confirm_frames == 5
        assert config.test_max_frames == 100


class TestSettingsConfiguration:
    """Test settings configuration loading."""
    
    def test_phone_settings_exist(self):
        """Test that phone detection settings are defined in Settings."""
        settings = Settings()
        assert hasattr(settings, 'PHONE_DETECTION_ENABLED')
        assert hasattr(settings, 'PHONE_MODEL_PATH')
        assert hasattr(settings, 'PHONE_CLASS_NAME')
        assert hasattr(settings, 'PHONE_CONFIDENCE')
        assert hasattr(settings, 'PHONE_IMAGE_SIZE')
        assert hasattr(settings, 'PHONE_FALLBACK_IMAGE_SIZES')
        assert hasattr(settings, 'PHONE_MIN_BOX_AREA')
        assert hasattr(settings, 'PHONE_ROI_ENABLED')
        assert hasattr(settings, 'PHONE_ROI_EXPANSION')
        assert hasattr(settings, 'PHONE_TEMPORAL_CONFIRM_FRAMES')
        assert hasattr(settings, 'PHONE_TEMPORAL_MAX_MISSED_FRAMES')
        assert hasattr(settings, 'PHONE_ASSOCIATION_IOU')
        assert hasattr(settings, 'PHONE_DEDUPLICATION_IOU')
        assert hasattr(settings, 'PHONE_DEBUG_ENABLED')
        assert hasattr(settings, 'PHONE_DEBUG_MAX_FRAMES')
        assert hasattr(settings, 'PHONE_RAW_DEBUG_CONFIDENCE')
        assert hasattr(settings, 'PHONE_RAW_DEBUG_IMAGE_SIZE')
        assert hasattr(settings, 'PHONE_TEST_MAX_FRAMES')
        assert hasattr(settings, 'PHONE_TEST_START_FRAME')
        assert hasattr(settings, 'PHONE_TEST_END_FRAME')
        assert hasattr(settings, 'PHONE_TEST_FRAME_STEP')
    
    def test_phone_settings_defaults(self):
        """Test that phone detection settings have correct defaults."""
        settings = Settings()
        assert settings.PHONE_DETECTION_ENABLED is True
        assert settings.PHONE_MODEL_PATH == ""
        assert settings.PHONE_CLASS_NAME == "cell phone"
        assert settings.PHONE_CONFIDENCE == 0.10
        assert settings.PHONE_IMAGE_SIZE == 960
        assert settings.PHONE_FALLBACK_IMAGE_SIZES == "768,640"
        assert settings.PHONE_MIN_BOX_AREA == 10
        assert settings.PHONE_ROI_ENABLED is True
        assert settings.PHONE_ROI_EXPANSION == 0.15
        assert settings.PHONE_TEMPORAL_CONFIRM_FRAMES == 3
        assert settings.PHONE_TEMPORAL_MAX_MISSED_FRAMES == 2
        assert settings.PHONE_ASSOCIATION_IOU == 0.10
        assert settings.PHONE_DEDUPLICATION_IOU == 0.50
        assert settings.PHONE_DEBUG_ENABLED is False
        assert settings.PHONE_DEBUG_MAX_FRAMES == 20
        assert settings.PHONE_RAW_DEBUG_CONFIDENCE == 0.01
        assert settings.PHONE_RAW_DEBUG_IMAGE_SIZE == 1280
        assert settings.PHONE_TEST_MAX_FRAMES == 0
        assert settings.PHONE_TEST_START_FRAME == 0
        assert settings.PHONE_TEST_END_FRAME == 0
        assert settings.PHONE_TEST_FRAME_STEP == 1
    
    def test_fallback_image_sizes_parsing(self):
        """Test that fallback image sizes parse correctly."""
        settings = Settings()
        fallback_sizes = [int(x) for x in settings.PHONE_FALLBACK_IMAGE_SIZES.split(",")]
        assert fallback_sizes == [768, 640]
        assert len(fallback_sizes) == 2
        assert all(isinstance(x, int) for x in fallback_sizes)


class TestDeviceResolver:
    """Test device resolution utility."""
    
    def test_auto_selects_cuda_when_available(self, monkeypatch):
        """Test auto selects CUDA when available."""
        monkeypatch.setattr("torch.cuda.is_available", lambda: True)
        monkeypatch.setattr("torch.cuda.get_device_name", lambda x: "Test GPU")
        device = resolve_device("auto")
        assert device == "cuda:0"
    
    def test_auto_selects_cpu_when_cuda_unavailable(self, monkeypatch):
        """Test auto selects CPU when CUDA unavailable."""
        monkeypatch.setattr("torch.cuda.is_available", lambda: False)
        device = resolve_device("auto")
        assert device == "cpu"
    
    def test_explicit_cpu(self):
        """Test explicit CPU selection."""
        device = resolve_device("cpu")
        assert device == "cpu"
    
    def test_cuda_fallback_when_unavailable(self, monkeypatch):
        """Test CUDA falls back to CPU when unavailable."""
        monkeypatch.setattr("torch.cuda.is_available", lambda: False)
        device = resolve_device("cuda:0")
        assert device == "cpu"


class TestPhoneTemporalTracker:
    """Test phone temporal tracking."""
    
    def test_initialization(self):
        """Test tracker initialization."""
        tracker = PhoneTemporalTracker(confirm_frames=3, max_missed_frames=2)
        assert tracker._confirm_frames == 3
        assert tracker._max_missed_frames == 2
        assert tracker._next_track_id == 1
        assert len(tracker._tracks) == 0
    
    def test_new_detection_creates_candidate_track(self):
        """Test new detection creates candidate track."""
        tracker = PhoneTemporalTracker()
        detections = [{"bbox": [10, 10, 50, 50], "confidence": 0.8}]
        
        confirmed = tracker.update(detections, frame_number=1)
        
        assert len(tracker._tracks) == 1
        assert tracker._tracks[1].state == PhoneState.CANDIDATE
        assert tracker._tracks[1].detection_count == 1
        assert len(confirmed) == 0  # Not confirmed yet
    
    def test_track_confirms_after_required_frames(self):
        """Test track confirms after required detections."""
        tracker = PhoneTemporalTracker(confirm_frames=2, max_missed_frames=2)
        detections = [{"bbox": [10, 10, 50, 50], "confidence": 0.8}]
        
        # First frame
        tracker.update(detections, frame_number=1)
        assert tracker._tracks[1].state == PhoneState.CANDIDATE
        
        # Second frame
        tracker.update(detections, frame_number=2)
        assert tracker._tracks[1].state == PhoneState.CONFIRMED
        
        confirmed = tracker.update(detections, frame_number=3)
        assert len(confirmed) == 1
    
    def test_track_survives_one_missed_frame(self):
        """Test track survives one missed frame."""
        tracker = PhoneTemporalTracker(confirm_frames=2, max_missed_frames=2)
        detections = [{"bbox": [10, 10, 50, 50], "confidence": 0.8}]
        
        # Confirm track
        tracker.update(detections, frame_number=1)
        tracker.update(detections, frame_number=2)
        assert tracker._tracks[1].state == PhoneState.CONFIRMED
        
        # Miss one frame
        confirmed = tracker.update([], frame_number=3)
        assert tracker._tracks[1].state == PhoneState.TEMPORARILY_MISSING
        assert tracker._tracks[1].missed_frames == 1
        assert len(confirmed) == 0  # Not confirmed while missing
        
        # Recover
        confirmed = tracker.update(detections, frame_number=4)
        assert tracker._tracks[1].state == PhoneState.CONFIRMED
        assert tracker._tracks[1].missed_frames == 0
        assert len(confirmed) == 1
    
    def test_track_expires_after_max_missed_frames(self):
        """Test track expires after max missed frames."""
        tracker = PhoneTemporalTracker(confirm_frames=2, max_missed_frames=2)
        detections = [{"bbox": [10, 10, 50, 50], "confidence": 0.8}]
        
        # Confirm track
        tracker.update(detections, frame_number=1)
        tracker.update(detections, frame_number=2)
        
        # Miss frames until expiration
        tracker.update([], frame_number=3)
        tracker.update([], frame_number=4)
        tracker.update([], frame_number=5)
        
        assert 1 not in tracker._tracks  # Track expired
    
    def test_reset_clears_all_tracks(self):
        """Test reset clears all tracking state."""
        tracker = PhoneTemporalTracker()
        detections = [{"bbox": [10, 10, 50, 50], "confidence": 0.8}]
        
        tracker.update(detections, frame_number=1)
        assert len(tracker._tracks) == 1
        
        tracker.reset()
        assert len(tracker._tracks) == 0
        assert tracker._next_track_id == 1
    
    def test_iou_calculation(self):
        """Test IoU calculation."""
        tracker = PhoneTemporalTracker()
        
        # Perfect overlap
        iou = tracker._calculate_iou([0, 0, 10, 10], [0, 0, 10, 10])
        assert iou == 1.0
        
        # No overlap
        iou = tracker._calculate_iou([0, 0, 10, 10], [20, 20, 30, 30])
        assert iou == 0.0
        
        # Partial overlap
        iou = tracker._calculate_iou([0, 0, 10, 10], [5, 5, 15, 15])
        assert 0 < iou < 1.0


class TestPhoneTrack:
    """Test PhoneTrack dataclass."""
    
    def test_track_creation(self):
        """Test track creation."""
        track = PhoneTrack(
            phone_track_id=1,
            bounding_box=[10, 10, 50, 50],
            confidence=0.8,
            student_track_id=5,
        )
        assert track.phone_track_id == 1
        assert track.bounding_box == [10, 10, 50, 50]
        assert track.confidence == 0.8
        assert track.student_track_id == 5
        assert track.state == PhoneState.CANDIDATE
        assert track.detection_count == 0
    
    def test_track_update(self):
        """Test track update."""
        track = PhoneTrack(
            phone_track_id=1,
            bounding_box=[10, 10, 50, 50],
            confidence=0.8,
        )
        
        track.update([15, 15, 55, 55], 0.9, frame_number=5)
        
        assert track.bounding_box == [15, 15, 55, 55]
        assert track.confidence == 0.9
        assert track.last_seen_frame == 5
        assert track.detection_count == 1
        assert track.missed_frames == 0
    
    def test_track_mark_missed(self):
        """Test marking track as missed."""
        track = PhoneTrack(
            phone_track_id=1,
            bounding_box=[10, 10, 50, 50],
            confidence=0.8,
        )
        
        track.mark_missed(frame_number=5)
        
        assert track.last_seen_frame == 5
        assert track.missed_frames == 1
    
    def test_should_confirm(self):
        """Test confirmation logic."""
        track = PhoneTrack(
            phone_track_id=1,
            bounding_box=[10, 10, 50, 50],
            confidence=0.8,
        )
        
        assert not track.should_confirm(confirm_frames=3)
        
        track.detection_count = 3
        assert track.should_confirm(confirm_frames=3)
    
    def test_should_expire(self):
        """Test expiration logic."""
        track = PhoneTrack(
            phone_track_id=1,
            bounding_box=[10, 10, 50, 50],
            confidence=0.8,
        )
        
        assert not track.should_expire(max_missed_frames=2)
        
        track.missed_frames = 3
        assert track.should_expire(max_missed_frames=2)


class TestPhoneDetectionService:
    """Test phone detection service."""
    
    def test_initialization_disabled(self):
        """Test initialization when disabled."""
        config = PhoneDetectionConfig(enabled=False)
        yolo_config = YOLOConfig(model_path="yolov8n.pt")
        
        service = PhoneDetectionService(config, yolo_config)
        service.initialize()
        
        assert service._initialized is True
    
    def test_class_id_resolution(self):
        """Test phone class ID resolution."""
        config = PhoneDetectionConfig(class_name="cell phone")
        yolo_config = YOLOConfig(model_path="yolov8n.pt")
        
        service = PhoneDetectionService(config, yolo_config)
        
        # Mock model with names
        mock_names = {0: "person", 67: "cell phone", 73: "book"}
        class_id = service._resolve_class_id(mock_names)
        
        assert class_id == 67
    
    def test_class_id_not_found(self):
        """Test handling when class ID not found."""
        config = PhoneDetectionConfig(class_name="cell phone")
        yolo_config = YOLOConfig(model_path="yolov8n.pt")
        
        service = PhoneDetectionService(config, yolo_config)
        
        # Mock model without phone class
        mock_names = {0: "person", 73: "book"}
        class_id = service._resolve_class_id(mock_names)
        
        assert class_id is None
    
    def test_iou_calculation(self):
        """Test IoU calculation in service."""
        config = PhoneDetectionConfig()
        yolo_config = YOLOConfig(model_path="yolov8n.pt")
        
        service = PhoneDetectionService(config, yolo_config)
        
        # Perfect overlap
        iou = service._calculate_iou([0, 0, 10, 10], [0, 0, 10, 10])
        assert iou == 1.0
        
        # No overlap
        iou = service._calculate_iou([0, 0, 10, 10], [20, 20, 30, 30])
        assert iou == 0.0
    
    def test_bbox_expansion(self):
        """Test bounding box expansion."""
        config = PhoneDetectionConfig(roi_expansion=0.2)
        yolo_config = YOLOConfig(model_path="yolov8n.pt")
        
        service = PhoneDetectionService(config, yolo_config)
        
        original = [10, 10, 50, 50]  # 40x40 box
        expanded = service._expand_bbox(original, 0.2)
        
        # Should be expanded by 20% on each side
        # Width/Height = 40, expansion = 8
        # New box should be [10-8, 10-8, 50+8, 50+8] = [2, 2, 58, 58]
        assert expanded == [2, 2, 58, 58]
    
    def test_point_in_bbox(self):
        """Test point in bounding box check."""
        config = PhoneDetectionConfig()
        yolo_config = YOLOConfig(model_path="yolov8n.pt")
        
        service = PhoneDetectionService(config, yolo_config)
        
        bbox = [10, 10, 50, 50]
        
        assert service._point_in_bbox([30, 30], bbox) is True  # Inside
        assert service._point_in_bbox([5, 5], bbox) is False   # Outside
        assert service._point_in_bbox([10, 10], bbox) is True  # On edge
    
    def test_reset(self):
        """Test service reset."""
        config = PhoneDetectionConfig()
        yolo_config = YOLOConfig(model_path="yolov8n.pt")
        
        service = PhoneDetectionService(config, yolo_config)
        service._temporal_tracker._tracks[1] = PhoneTrack(
            phone_track_id=1,
            bounding_box=[10, 10, 50, 50],
            confidence=0.8,
        )
        
        service.reset()
        
        assert len(service._temporal_tracker._tracks) == 0
        assert service._fallback_index == 0


class TestPhoneStudentAssociator:
    """Test phone-student association."""
    
    def test_initialization(self):
        """Test associator initialization."""
        associator = PhoneStudentAssociator()
        assert associator._roi_expansion == 0.15
        assert associator._association_iou == 0.10
        assert associator._association_switch_confirm_frames == 3
        assert associator._max_centre_distance == 100.0
        assert associator._min_association_score == 0.3
    
    def test_phone_center_inside_person_box(self):
        """Test phone centre inside person box associates correctly."""
        associator = PhoneStudentAssociator()
        
        # Phone inside person box
        phone_bbox = [100, 100, 150, 150]  # Phone at center of person
        person_bbox = [50, 50, 200, 200]   # Person box
        
        # Mock person track
        person_track = Mock()
        person_track.track_id = 1
        person_track.bbox = person_bbox
        person_track.is_confirmed = True
        
        phone_detections = [{"bbox": phone_bbox, "confidence": 0.8}]
        result = associator.associate(phone_detections, [person_track], 1920, 1080)
        
        assert result[0]["student_track_id"] == 1
        assert "center_inside" in result[0]["association_method"]
        assert result[0]["association_score"] >= 1.0
    
    def test_phone_just_outside_person_box_associates_through_expansion(self):
        """Test phone just outside original person box associates through expansion."""
        associator = PhoneStudentAssociator(roi_expansion=0.2)
        
        # Phone just outside person box but inside expanded
        phone_bbox = [210, 210, 260, 260]  # Just outside
        person_bbox = [50, 50, 200, 200]   # Person box
        
        person_track = Mock()
        person_track.track_id = 1
        person_track.bbox = person_bbox
        person_track.is_confirmed = True
        
        phone_detections = [{"bbox": phone_bbox, "confidence": 0.8}]
        result = associator.associate(phone_detections, [person_track], 1920, 1080)
        
        assert result[0]["student_track_id"] == 1
        # The phone is outside the original box but inside expanded, so it should associate
        assert result[0]["association_score"] > 0
    
    def test_phone_between_two_students_selects_stronger_association(self):
        """Test phone between two students selects the stronger association."""
        associator = PhoneStudentAssociator()
        
        phone_bbox = [150, 150, 200, 200]
        
        # Person 1: closer to phone
        person1 = Mock()
        person1.track_id = 1
        person1.bbox = [100, 100, 250, 250]
        person1.is_confirmed = True
        
        # Person 2: farther from phone
        person2 = Mock()
        person2.track_id = 2
        person2.bbox = [300, 300, 450, 450]
        person2.is_confirmed = True
        
        phone_detections = [{"bbox": phone_bbox, "confidence": 0.8}]
        result = associator.associate(phone_detections, [person1, person2], 1920, 1080)
        
        # Should associate with person 1 (closer)
        assert result[0]["student_track_id"] == 1
    
    def test_distant_unrelated_person_not_selected(self):
        """Test distant unrelated person is not selected."""
        associator = PhoneStudentAssociator(max_centre_distance=50.0)
        
        phone_bbox = [100, 100, 150, 150]
        
        # Distant person
        person = Mock()
        person.track_id = 1
        person.bbox = [500, 500, 600, 600]
        person.is_confirmed = True
        
        phone_detections = [{"bbox": phone_bbox, "confidence": 0.8}]
        result = associator.associate(phone_detections, [person], 1920, 1080)
        
        # Should not associate with distant person
        assert result[0]["student_track_id"] is None
        assert result[0]["association_method"] == "unknown"
    
    def test_no_valid_candidate_results_in_unknown(self):
        """Test no valid candidate results in student_track_id=None."""
        associator = PhoneStudentAssociator()
        
        phone_bbox = [100, 100, 150, 150]
        phone_detections = [{"bbox": phone_bbox, "confidence": 0.8}]
        
        result = associator.associate(phone_detections, [], 1920, 1080)
        
        assert result[0]["student_track_id"] is None
        assert result[0]["association_method"] == "unknown"
    
    def test_temporal_matching_keeps_same_student(self):
        """Test temporal matching keeps same student during missed frame."""
        associator = PhoneStudentAssociator()
        
        phone_bbox = [100, 100, 150, 150]
        person_bbox = [50, 50, 200, 200]
        
        person = Mock()
        person.track_id = 1
        person.bbox = person_bbox
        person.is_confirmed = True
        
        # First frame with association
        phone_detections = [
            {"bbox": phone_bbox, "confidence": 0.8, "phone_track_id": 1, "student_track_id": 1}
        ]
        result = associator.associate(phone_detections, [person], 1920, 1080, frame_number=1)
        
        assert result[0]["student_track_id"] == 1
        
        # Second frame with same association
        phone_detections = [
            {"bbox": phone_bbox, "confidence": 0.8, "phone_track_id": 1, "student_track_id": 1}
        ]
        result = associator.associate(phone_detections, [person], 1920, 1080, frame_number=2)
        
        assert result[0]["student_track_id"] == 1
    
    def test_association_does_not_flicker_between_nearby_students(self):
        """Test association does not flicker between nearby students."""
        associator = PhoneStudentAssociator(association_switch_confirm_frames=3)
        
        phone_bbox = [150, 150, 200, 200]
        
        # Two nearby students
        person1 = Mock()
        person1.track_id = 1
        person1.bbox = [100, 100, 250, 250]
        person1.is_confirmed = True
        
        person2 = Mock()
        person2.track_id = 2
        person2.bbox = [120, 120, 270, 270]
        person2.is_confirmed = True
        
        # Initially associated with student 1
        phone_detections = [
            {"bbox": phone_bbox, "confidence": 0.8, "phone_track_id": 1, "student_track_id": 1}
        ]
        result = associator.associate(phone_detections, [person1, person2], 1920, 1080, frame_number=1)
        
        assert result[0]["student_track_id"] == 1
        
        # Student 2 has slightly better score but not enough frames to switch
        phone_detections = [
            {"bbox": phone_bbox, "confidence": 0.8, "phone_track_id": 1, "student_track_id": 1}
        ]
        result = associator.associate(phone_detections, [person1, person2], 1920, 1080, frame_number=2)
        
        # Should still be student 1 (temporal persistence)
        assert result[0]["student_track_id"] == 1
    
    def test_unconfirmed_tracks_ignored(self):
        """Test unconfirmed DeepSORT tracks with no hits are ignored."""
        associator = PhoneStudentAssociator()

        phone_bbox = [100, 100, 150, 150]

        # Unconfirmed person track with no hits (truly new track)
        person = Mock()
        person.track_id = 1
        person.bbox = [50, 50, 200, 200]
        person.is_confirmed = False
        person.hits = 0

        phone_detections = [{"bbox": phone_bbox, "confidence": 0.8}]
        result = associator.associate(phone_detections, [person], 1920, 1080)

        # Should not associate with unconfirmed track with no hits
        assert result[0]["student_track_id"] is None

    def test_unconfirmed_track_with_hits_associated(self):
        """Test unconfirmed tracks with at least 1 hit are eligible for association."""
        associator = PhoneStudentAssociator()

        phone_bbox = [100, 100, 150, 150]

        # Unconfirmed person track with 1 hit (new but has detection)
        person = Mock()
        person.track_id = 0
        person.bbox = [50, 50, 200, 200]
        person.is_confirmed = False
        person.hits = 1

        phone_detections = [{"bbox": phone_bbox, "confidence": 0.8}]
        result = associator.associate(phone_detections, [person], 1920, 1080)

        # Should associate with unconfirmed track that has at least 1 hit
        assert result[0]["student_track_id"] == 0
    
    def test_iou_calculation(self):
        """Test IoU calculation."""
        associator = PhoneStudentAssociator()
        
        # Perfect overlap
        iou = associator._calculate_iou([0, 0, 10, 10], [0, 0, 10, 10])
        assert iou == 1.0
        
        # No overlap
        iou = associator._calculate_iou([0, 0, 10, 10], [20, 20, 30, 30])
        assert iou == 0.0
        
        # Partial overlap
        iou = associator._calculate_iou([0, 0, 10, 10], [5, 5, 15, 15])
        assert 0 < iou < 1.0
    
    def test_intersection_over_phone_area(self):
        """Test intersection over phone area calculation."""
        associator = PhoneStudentAssociator()
        
        # Phone completely inside person
        overlap = associator._calculate_intersection_over_phone_area(
            [5, 5, 10, 10],  # Phone
            [0, 0, 20, 20]   # Person
        )
        assert overlap == 1.0
        
        # Partial overlap
        overlap = associator._calculate_intersection_over_phone_area(
            [0, 0, 10, 10],  # Phone
            [5, 5, 15, 15]   # Person
        )
        assert 0 < overlap < 1.0
    
    def test_bbox_expansion(self):
        """Test bounding box expansion."""
        associator = PhoneStudentAssociator()
        
        original = [10, 10, 50, 50]
        expanded = associator._expand_bbox(original, 0.2, 1000, 1000)
        
        # Should be expanded by 20%
        assert expanded[0] < original[0]  # x1 decreased
        assert expanded[1] < original[1]  # y1 decreased
        assert expanded[2] > original[2]  # x2 increased
        assert expanded[3] > original[3]  # y2 increased
    
    def test_point_in_bbox(self):
        """Test point in bounding box check."""
        associator = PhoneStudentAssociator()
        
        bbox = [10, 10, 50, 50]
        
        assert associator._point_in_bbox((30, 30), bbox) is True
        assert associator._point_in_bbox((5, 5), bbox) is False
        assert associator._point_in_bbox((10, 10), bbox) is True
    
    def test_reset(self):
        """Test associator reset."""
        associator = PhoneStudentAssociator()
        
        # Add a pending switch
        associator._pending_switches[1] = (2, 2)
        
        associator.reset()
        
        assert len(associator._pending_switches) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
