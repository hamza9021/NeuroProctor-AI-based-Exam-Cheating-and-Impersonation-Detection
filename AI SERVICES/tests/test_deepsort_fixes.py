"""Unit tests for DeepSORT tracking fixes."""

import asyncio
import numpy as np
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch, MagicMock

import pytest

from app.services.ai.pipeline.context import Detection, FrameContext
from app.services.ai.trackers.deepsort.annotator import TrackAnnotator
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.service import DeepSORTService
from app.services.ai.trackers.deepsort.track import Track
from app.services.ai.trackers.deepsort.track_state_manager import TrackStateManager
from app.services.ai.trackers.deepsort.validator import DetectionValidator
from app.services.ai.monitoring import PipelineLogger


class TestTrackAnnotator:
    """Tests for TrackAnnotator color selection."""
    
    def test_color_selection_normal_id(self):
        """Test color selection with normal track IDs."""
        annotator = TrackAnnotator()
        color = annotator._get_track_color(0)
        assert color == (0, 255, 0)  # First color in palette
        
        color = annotator._get_track_color(1)
        assert color == (255, 0, 0)  # Second color in palette
    
    def test_color_cycling_large_id(self):
        """Test color cycling for IDs larger than palette."""
        annotator = TrackAnnotator()
        palette_size = len(annotator._color_map)
        
        # ID larger than palette should cycle
        color = annotator._get_track_color(palette_size + 2)
        assert color == (0, 0, 255)  # Third color in palette
    
    def test_empty_color_map_fallback(self):
        """Test empty color map fallback to green."""
        annotator = TrackAnnotator()
        annotator._color_map = []
        
        color = annotator._get_track_color(0)
        assert color == (0, 255, 0)
    
    def test_negative_track_id(self):
        """Test negative track ID doesn't cause index error."""
        annotator = TrackAnnotator()
        color = annotator._get_track_color(-1)
        # Should handle negative ID gracefully
        assert isinstance(color, tuple)
        assert len(color) == 3


class TestDetectionValidator:
    """Tests for DetectionValidator statistics and logging."""
    
    def test_correct_ignored_detection_count(self):
        """Test ignored detection count matches actual filtered count."""
        validator = DetectionValidator()
        
        detections = [
            Detection(None, "person", 0, 0.9, [100, 100, 200, 300], [150, 200], 100, 200),
            Detection(None, "person", 0, 0.8, [100, 100, 200, 300], [150, 200], 100, 200),
            Detection(None, "cell phone", 0, 0.9, [100, 100, 200, 300], [150, 200], 100, 200),
            Detection(None, "person", 0, 0.1, [100, 100, 200, 300], [150, 200], 100, 200),  # Low confidence
        ]
        
        valid_detections, stats = validator.validate(detections, 0.5)
        
        assert stats["total_detections"] == 4
        assert stats["valid_person_detections"] == 2
        assert stats["invalid_person_detections"] == 1
        assert stats["non_person_detections"] == 1
    
    def test_invalid_bbox_reason_logging(self):
        """Test invalid detection includes useful rejection reason."""
        validator = DetectionValidator()
        
        # Test negative coordinates
        det = Detection(None, "person", 0, 0.9, [-10, 100, 200, 300], [150, 200], 100, 200)
        result = validator._is_valid_bbox(det.bbox)
        assert "negative coordinates" in result
        
        # Test invalid width
        det = Detection(None, "person", 0, 0.9, [200, 100, 100, 300], [150, 200], 100, 200)
        result = validator._is_valid_bbox(det.bbox)
        assert "width must be positive" in result
        
        # Test non-finite values
        det = Detection(None, "person", 0, 0.9, [float('inf'), 100, 200, 300], [150, 200], 100, 200)
        result = validator._is_valid_bbox(det.bbox)
        assert "non-finite" in result
    
    def test_confidence_below_threshold_reason(self):
        """Test confidence below threshold returns specific reason."""
        validator = DetectionValidator()
        
        det = Detection(None, "person", 0, 0.1, [100, 100, 200, 300], [150, 200], 100, 200)
        result = validator._is_valid_detection(det, 0.5)
        assert "below threshold" in result
    
    def test_center_point_missing_reason(self):
        """Test missing center point returns specific reason."""
        validator = DetectionValidator()
        
        det = Detection(None, "person", 0, 0.9, [100, 100, 200, 300], None, 100, 200)
        result = validator._is_valid_detection(det, 0.5)
        assert "center point missing" in result


class TestTrackStateManager:
    """Tests for TrackStateManager recovery event logic."""
    
    def test_track_created_on_new_track(self):
        """Test created event emitted for new track."""
        manager = TrackStateManager()
        
        transitions = manager.update_state(0, False, 0, 1, 1)
        assert transitions["created"] is True
        assert transitions["recovered"] is False
    
    def test_track_recovered_on_state_transition(self):
        """Test recovered event only on lost -> active transition."""
        manager = TrackStateManager()
        
        # Track becomes lost
        manager.update_state(0, True, 1, 5, 5)
        
        # Track recovers
        transitions = manager.update_state(0, True, 0, 6, 6)
        assert transitions["recovered"] is True
        assert transitions["created"] is False
    
    def test_no_recovered_event_for_active_track(self):
        """Test recovered event not emitted for always-active track."""
        manager = TrackStateManager()
        
        # First update (created)
        manager.update_state(0, True, 0, 1, 1)
        
        # Second update (still active)
        transitions = manager.update_state(0, True, 0, 2, 2)
        assert transitions["recovered"] is False
        assert transitions["updated"] is True
    
    def test_no_recovery_event_for_new_track(self):
        """Test recovery event not emitted for newly created track."""
        manager = TrackStateManager()
        
        transitions = manager.update_state(0, True, 0, 1, 1)
        assert transitions["recovered"] is False
        assert transitions["created"] is True


class TestAnnotationErrorHandling:
    """Tests for annotation error handling and tracking preservation."""
    
    @pytest.mark.asyncio
    async def test_tracking_succeeds_when_annotation_fails(self):
        """Test successful tracking preserves context when annotation fails."""
        config = DeepSORTConfig(annotation_required=False)
        mock_logger = Mock(spec=PipelineLogger)
        mock_logger.info = AsyncMock(return_value=None)
        mock_logger.warning = AsyncMock(return_value=None)
        
        service = DeepSORTService(config, mock_logger)
        service._initialized = True
        service._tracker = Mock()
        service._tracker.update = Mock(return_value=[])
        
        # Mock annotator to fail
        service._annotator.annotate = Mock(side_effect=Exception("Annotation error"))
        
        # Create context
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        context = FrameContext(frame=frame, frame_number=1, timestamp=datetime.now())
        context.detections = []
        
        # Process should not raise error
        result = await service.track(context)
        
        # Context should be preserved
        assert result is not None
        assert result.frame is not None
    
    @pytest.mark.asyncio
    async def test_original_frame_preserved_after_annotation_failure(self):
        """Test original frame preserved when annotation fails."""
        config = DeepSORTConfig(annotation_required=False)
        mock_logger = Mock(spec=PipelineLogger)
        mock_logger.info = AsyncMock(return_value=None)
        mock_logger.warning = AsyncMock(return_value=None)
        
        service = DeepSORTService(config, mock_logger)
        service._initialized = True
        service._tracker = Mock()
        service._tracker.update = Mock(return_value=[])
        
        original_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        original_frame[100, 100] = [255, 0, 0]  # Mark pixel
        
        # Mock annotator to fail
        service._annotator.annotate = Mock(side_effect=Exception("Annotation error"))
        
        context = FrameContext(frame=original_frame.copy(), frame_number=1, timestamp=datetime.now())
        context.detections = []
        
        result = await service.track(context)
        
        # Original frame should be preserved
        assert np.array_equal(result.frame, original_frame)
    
    @pytest.mark.asyncio
    async def test_framecontext_tracks_preserved_after_annotation_failure(self):
        """Test FrameContext.tracks preserved when annotation fails."""
        config = DeepSORTConfig(annotation_required=False)
        mock_logger = Mock(spec=PipelineLogger)
        mock_logger.info = AsyncMock(return_value=None)
        mock_logger.warning = AsyncMock(return_value=None)
        
        service = DeepSORTService(config, mock_logger)
        service._initialized = True
        service._tracker = Mock()
        
        # Mock tracker to return tracks
        mock_track = {
            'track_id': 0,
            'bbox': [100, 100, 200, 300],
            'centroid': [150, 200],
            'is_confirmed': True,
            'age': 5,
            'hits': 5,
            'time_since_update': 0,
        }
        service._tracker.update = Mock(return_value=[mock_track])
        
        # Mock annotator to fail
        service._annotator.annotate = Mock(side_effect=Exception("Annotation error"))
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        context = FrameContext(frame=frame, frame_number=1, timestamp=datetime.now())
        context.detections = [
            Detection(None, "person", 0, 0.9, [100, 100, 200, 300], [150, 200], 100, 200)
        ]
        
        result = await service.track(context)
        
        # Tracks should be preserved
        assert len(result.tracks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
