"""Temporal phone tracker for consistent phone detection across frames."""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class PhoneState(Enum):
    """Phone tracking states."""
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    TEMPORARILY_MISSING = "temporarily_missing"
    EXPIRED = "expired"


@dataclass
class PhoneTrack:
    """Represents a tracked phone across frames."""
    
    phone_track_id: int
    bounding_box: List[float]
    confidence: float
    student_track_id: Optional[int] = None
    association_score: float = 0.0
    association_method: str = "unknown"
    first_seen_frame: int = 0
    last_seen_frame: int = 0
    detection_count: int = 0
    missed_frames: int = 0
    state: PhoneState = PhoneState.CANDIDATE
    
    def update(self, bbox: List[float], confidence: float, frame_number: int, student_id: Optional[int] = None, association_score: float = 0.0, association_method: str = "unknown"):
        """Update track with new detection.
        
        Args:
            bbox: New bounding box.
            confidence: New confidence.
            frame_number: Current frame number.
            student_id: Associated student track ID.
            association_score: Association score.
            association_method: Association method.
        """
        self.bounding_box = bbox
        self.confidence = confidence
        self.last_seen_frame = frame_number
        self.detection_count += 1
        self.missed_frames = 0
        if student_id is not None:
            self.student_track_id = student_id
        self.association_score = association_score
        self.association_method = association_method
    
    def mark_missed(self, frame_number: int):
        """Mark track as missed in current frame.
        
        Args:
            frame_number: Current frame number.
        """
        self.last_seen_frame = frame_number
        self.missed_frames += 1
    
    def should_confirm(self, confirm_frames: int) -> bool:
        """Check if track should be confirmed.
        
        Args:
            confirm_frames: Required frames to confirm.
            
        Returns:
            True if track should be confirmed.
        """
        return self.detection_count >= confirm_frames
    
    def should_expire(self, max_missed_frames: int) -> bool:
        """Check if track should expire.
        
        Args:
            max_missed_frames: Max allowed missed frames.
            
        Returns:
            True if track should expire.
        """
        return self.missed_frames > max_missed_frames


class PhoneTemporalTracker:
    """Manages temporal tracking of phone detections."""
    
    def __init__(self, confirm_frames: int = 3, max_missed_frames: int = 2):
        """Initialize temporal tracker.
        
        Args:
            confirm_frames: Frames to confirm a phone detection.
            max_missed_frames: Max missed frames before expiration.
        """
        self._confirm_frames = confirm_frames
        self._max_missed_frames = max_missed_frames
        self._tracks: Dict[int, PhoneTrack] = {}
        self._next_track_id = 1
    
    def update(
        self,
        detections: List[dict],
        frame_number: int,
        student_tracks: List[dict] = None,
    ) -> List[PhoneTrack]:
        """Update temporal tracking with new detections.
        
        Args:
            detections: List of phone detections with bbox, confidence.
            frame_number: Current frame number.
            student_tracks: List of student tracks for association.
            
        Returns:
            List of confirmed phone tracks.
        """
        student_tracks = student_tracks or []
        
        # Mark all existing tracks as missed initially
        for track in self._tracks.values():
            track.mark_missed(frame_number)
        
        # Match new detections to existing tracks
        matched_track_ids = set()
        
        for detection in detections:
            bbox = detection.get("bbox", [])
            confidence = detection.get("confidence", 0.0)
            student_id = detection.get("student_track_id")
            association_score = detection.get("association_score", 0.0)
            association_method = detection.get("association_method", "unknown")
            
            # Find best matching existing track
            best_match_id = self._find_best_match(bbox, student_id)
            
            if best_match_id is not None:
                # Update existing track
                track = self._tracks[best_match_id]
                track.update(bbox, confidence, frame_number, student_id, association_score, association_method)
                matched_track_ids.add(best_match_id)
            else:
                # Create new track
                new_track = PhoneTrack(
                    phone_track_id=self._next_track_id,
                    bounding_box=bbox,
                    confidence=confidence,
                    student_track_id=student_id,
                    association_score=association_score,
                    association_method=association_method,
                    first_seen_frame=frame_number,
                    last_seen_frame=frame_number,
                    detection_count=1,
                    state=PhoneState.CANDIDATE,
                )
                self._tracks[self._next_track_id] = new_track
                self._next_track_id += 1
        
        # Update states
        confirmed_tracks = []
        expired_track_ids = []
        
        for track_id, track in self._tracks.items():
            if track_id in matched_track_ids:
                # Track was updated this frame
                if track.state == PhoneState.CANDIDATE and track.should_confirm(self._confirm_frames):
                    track.state = PhoneState.CONFIRMED
                    logger.info(f"Phone track {track_id} confirmed after {track.detection_count} detections")
                elif track.state == PhoneState.TEMPORARILY_MISSING:
                    track.state = PhoneState.CONFIRMED
            else:
                # Track was missed this frame
                if track.state == PhoneState.CONFIRMED:
                    track.state = PhoneState.TEMPORARILY_MISSING
                elif track.state == PhoneState.TEMPORARILY_MISSING and track.should_expire(self._max_missed_frames):
                    track.state = PhoneState.EXPIRED
                    expired_track_ids.append(track_id)
            
            # Collect confirmed tracks
            if track.state == PhoneState.CONFIRMED:
                confirmed_tracks.append(track)
        
        # Remove expired tracks
        for track_id in expired_track_ids:
            del self._tracks[track_id]
            logger.info(f"Phone track {track_id} expired after {self._max_missed_frames} missed frames")
        
        return confirmed_tracks
    
    def _find_best_match(self, bbox: List[float], student_id: Optional[int]) -> Optional[int]:
        """Find best matching existing track for a detection.
        
        Args:
            bbox: Detection bounding box.
            student_id: Associated student track ID.
            
        Returns:
            Best matching track ID or None.
        """
        best_match_id = None
        best_iou = 0.0
        
        for track_id, track in self._tracks.items():
            if track.state == PhoneState.EXPIRED:
                continue
            
            # Prefer same student track
            if student_id is not None and track.student_track_id == student_id:
                iou = self._calculate_iou(bbox, track.bounding_box)
                if iou > best_iou and iou > 0.1:
                    best_iou = iou
                    best_match_id = track_id
            elif student_id is None:
                # No student association, use IoU only
                iou = self._calculate_iou(bbox, track.bounding_box)
                if iou > best_iou and iou > 0.3:
                    best_iou = iou
                    best_match_id = track_id
        
        return best_match_id
    
    def _calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Calculate IoU between two bounding boxes.
        
        Args:
            bbox1: First bounding box [x1, y1, x2, y2].
            bbox2: Second bounding box [x1, y1, x2, y2].
            
        Returns:
            IoU value.
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = area1 + area2 - intersection_area
        
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area
    
    def reset(self):
        """Reset all tracking state."""
        self._tracks.clear()
        self._next_track_id = 1
        logger.info("Phone temporal tracker reset")
