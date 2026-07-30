"""Phone-to-student association service."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AssociationResult:
    """Result of phone-to-student association.
    
    Attributes:
        student_track_id: Associated DeepSORT person track ID.
        association_score: Combined association score.
        association_method: Method used for association.
        center_inside: Phone centre inside original person box.
        expanded_center_inside: Phone centre inside expanded person box.
        phone_area_overlap: Intersection over phone area.
        normal_iou: Normal IoU between boxes.
        centre_distance: Distance from phone centre to person centre.
    """
    student_track_id: Optional[int]
    association_score: float
    association_method: str
    center_inside: bool = False
    expanded_center_inside: bool = False
    phone_area_overlap: float = 0.0
    normal_iou: float = 0.0
    centre_distance: float = 0.0


class PhoneStudentAssociator:
    """Associates phone detections with DeepSORT person tracks."""
    
    def __init__(
        self,
        roi_expansion: float = 0.15,
        association_iou: float = 0.10,
        association_switch_confirm_frames: int = 3,
        association_switch_margin: float = 0.20,
        max_centre_distance: float = 100.0,
        min_association_score: float = 0.3,
    ):
        """Initialize phone-student associator.
        
        Args:
            roi_expansion: ROI expansion factor for person boxes.
            association_iou: Minimum IoU threshold for association.
            association_switch_confirm_frames: Frames to confirm student switch.
            association_switch_margin: Score margin to switch students.
            max_centre_distance: Maximum centre distance for association.
            min_association_score: Minimum score to accept association.
        """
        self._roi_expansion = roi_expansion
        self._association_iou = association_iou
        self._association_switch_confirm_frames = association_switch_confirm_frames
        self._association_switch_margin = association_switch_margin
        self._max_centre_distance = max_centre_distance
        self._min_association_score = min_association_score
        
        # Temporal tracking for student switches
        self._pending_switches: dict[int, Tuple[int, int]] = {}  # phone_id -> (new_student_id, frame_count)
    
    def associate(
        self,
        phone_detections: List[dict],
        person_tracks: List,
        frame_width: int,
        frame_height: int,
        frame_number: int = 0,
    ) -> List[dict]:
        """Associate phone detections with person tracks.
        
        Args:
            phone_detections: List of phone detection dictionaries.
            person_tracks: List of DeepSORT person tracks.
            frame_width: Frame width.
            frame_height: Frame height.
            frame_number: Current frame number.
            
        Returns:
            List of phone detections with student_track_id added.
        """
        # Filter for confirmed person tracks or tracks with at least 1 hit
        # This allows association with new tracks before they're fully confirmed
        eligible_tracks = []
        for t in person_tracks:
            is_confirmed = getattr(t, 'is_confirmed', True)
            hits = getattr(t, 'hits', 0)
            # Include if confirmed OR has at least 1 hit (real detection)
            # Handle case where hits might be a Mock object in tests
            if is_confirmed or (isinstance(hits, int) and hits >= 1):
                eligible_tracks.append(t)
        
        for phone in phone_detections:
            phone_bbox = phone.get("bbox", [0, 0, 0, 0])
            phone_track_id = phone.get("phone_track_id")
            previous_student_id = phone.get("student_track_id")
            
            # Calculate association with all person tracks
            results = []
            for track in eligible_tracks:
                result = self._calculate_association(
                    phone_bbox,
                    track.bbox,
                    track.track_id,
                    frame_width,
                    frame_height,
                )
                if result.association_score > 0:
                    results.append(result)
            
            # Select best association
            if results:
                best_result = max(results, key=lambda r: r.association_score)
                
                # Check temporal switching logic
                if phone_track_id is not None and previous_student_id is not None:
                    if best_result.student_track_id != previous_student_id:
                        # Check if we should switch
                        if self._should_switch_student(
                            phone_track_id,
                            previous_student_id,
                            best_result.student_track_id,
                            best_result.association_score,
                        ):
                            # Update pending switch
                            self._pending_switches[phone_track_id] = (
                                best_result.student_track_id,
                                self._pending_switches.get(phone_track_id, (best_result.student_track_id, 0))[1] + 1,
                            )
                            
                            # Only apply after confirmation frames
                            if self._pending_switches[phone_track_id][1] >= self._association_switch_confirm_frames:
                                phone["student_track_id"] = best_result.student_track_id
                                phone["association_score"] = best_result.association_score
                                phone["association_method"] = best_result.association_method
                                del self._pending_switches[phone_track_id]
                                logger.debug(
                                    f"Phone track {phone_track_id} switched to student {best_result.student_track_id} "
                                    f"after {self._association_switch_confirm_frames} frames"
                                )
                            else:
                                # Keep previous student
                                phone["student_track_id"] = previous_student_id
                                phone["association_score"] = best_result.association_score
                                phone["association_method"] = "temporal_persistence"
                        else:
                            # Keep previous student
                            phone["student_track_id"] = previous_student_id
                            phone["association_score"] = best_result.association_score
                            phone["association_method"] = "temporal_persistence"
                    else:
                        # Same student, update
                        phone["student_track_id"] = best_result.student_track_id
                        phone["association_score"] = best_result.association_score
                        phone["association_method"] = best_result.association_method
                        # Clear pending switches
                        if phone_track_id in self._pending_switches:
                            del self._pending_switches[phone_track_id]
                else:
                    # No previous association, apply if score is high enough
                    if best_result.association_score >= self._min_association_score:
                        phone["student_track_id"] = best_result.student_track_id
                        phone["association_score"] = best_result.association_score
                        phone["association_method"] = best_result.association_method
                    else:
                        phone["student_track_id"] = None
                        phone["association_score"] = 0.0
                        phone["association_method"] = "unknown"
                
                # Log association details
                if phone["student_track_id"] is not None:
                    logger.debug(
                        f"Phone associated with student {phone['student_track_id']}, "
                        f"score={phone['association_score']:.2f}, method={phone['association_method']}"
                    )
                    
                    # Detailed logging for first association or changes
                    if phone_track_id is not None and frame_number % 10 == 0:  # Rate-limited
                        logger.info(
                            f"Phone track {phone_track_id} -> Student {phone['student_track_id']}, "
                            f"score={phone['association_score']:.2f}, "
                            f"method={phone['association_method']}, "
                            f"center_inside={best_result.center_inside}, "
                            f"expanded_inside={best_result.expanded_center_inside}, "
                            f"phone_area_overlap={best_result.phone_area_overlap:.2f}, "
                            f"iou={best_result.normal_iou:.2f}, "
                            f"distance={best_result.centre_distance:.1f}"
                        )
            else:
                # No valid association
                phone["student_track_id"] = None
                phone["association_score"] = 0.0
                phone["association_method"] = "unknown"
        
        return phone_detections
    
    def _calculate_association(
        self,
        phone_bbox: List[float],
        person_bbox: List[float],
        person_track_id: int,
        frame_width: int,
        frame_height: int,
    ) -> AssociationResult:
        """Calculate association score between phone and person.
        
        Args:
            phone_bbox: Phone bounding box [x1, y1, x2, y2].
            person_bbox: Person bounding box [x1, y1, x2, y2].
            person_track_id: Person track ID.
            frame_width: Frame width.
            frame_height: Frame height.
            
        Returns:
            AssociationResult with scoring details.
        """
        # Calculate centres
        phone_center = self._get_center(phone_bbox)
        person_center = self._get_center(person_bbox)
        
        # Calculate expanded person box
        expanded_person = self._expand_bbox(person_bbox, self._roi_expansion, frame_width, frame_height)
        
        # Check if phone centre inside original person box
        center_inside = self._point_in_bbox(phone_center, person_bbox)
        
        # Check if phone centre inside expanded person box
        expanded_center_inside = self._point_in_bbox(phone_center, expanded_person)
        
        # Calculate IoU metrics
        normal_iou = self._calculate_iou(phone_bbox, expanded_person)
        phone_area_overlap = self._calculate_intersection_over_phone_area(phone_bbox, expanded_person)
        
        # Calculate centre distance
        centre_distance = np.sqrt(
            (phone_center[0] - person_center[0])**2 +
            (phone_center[1] - person_center[1])**2
        )
        
        # Calculate combined score
        score = 0.0
        method = "unknown"
        
        if center_inside:
            score += 1.0
            method = "center_inside"
        elif expanded_center_inside:
            score += 0.8
            method = "expanded_center_inside"
        
        if phone_area_overlap > self._association_iou:
            score += 0.7
            if method == "unknown":
                method = "phone_area_overlap"
            else:
                method += "_and_area_overlap"
        
        if normal_iou > self._association_iou:
            score += 0.5
        
        # Distance score (inverse of distance)
        if centre_distance < self._max_centre_distance:
            distance_score = 1.0 - (centre_distance / self._max_centre_distance)
            score += distance_score * 0.3
            if method == "unknown":
                method = "nearest_valid_student"
        
        # Normalize score
        score = min(score, 1.0)
        
        return AssociationResult(
            student_track_id=person_track_id,
            association_score=score,
            association_method=method,
            center_inside=center_inside,
            expanded_center_inside=expanded_center_inside,
            phone_area_overlap=phone_area_overlap,
            normal_iou=normal_iou,
            centre_distance=centre_distance,
        )
    
    def _should_switch_student(
        self,
        phone_track_id: int,
        previous_student_id: int,
        new_student_id: int,
        new_score: float,
    ) -> bool:
        """Determine if we should switch to a different student.
        
        Args:
            phone_track_id: Phone track ID.
            previous_student_id: Previous associated student ID.
            new_student_id: New candidate student ID.
            new_score: New association score.
            
        Returns:
            True if switch should proceed.
        """
        # Check if there's a pending switch
        if phone_track_id in self._pending_switches:
            pending_student, frame_count = self._pending_switches[phone_track_id]
            if pending_student == new_student_id:
                # Continue with pending switch
                return True
            else:
                # Different student, reset
                del self._pending_switches[phone_track_id]
                return False
        
        # Only switch if new score is significantly better
        # We don't have the previous score, so assume switch is valid
        # In practice, you'd want to track previous scores
        return True
    
    def _get_center(self, bbox: List[float]) -> Tuple[float, float]:
        """Get center point of bounding box.
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2].
            
        Returns:
            Center (x, y).
        """
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def _expand_bbox(
        self,
        bbox: List[float],
        expansion: float,
        frame_width: int,
        frame_height: int,
    ) -> List[float]:
        """Expand bounding box by factor.
        
        Args:
            bbox: Original bounding box.
            expansion: Expansion factor.
            frame_width: Frame width for clipping.
            frame_height: Frame height for clipping.
            
        Returns:
            Expanded bounding box.
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        expand_x = width * expansion
        expand_y = height * expansion
        
        new_x1 = max(0, x1 - expand_x)
        new_y1 = max(0, y1 - expand_y)
        new_x2 = min(frame_width, x2 + expand_x)
        new_y2 = min(frame_height, y2 + expand_y)
        
        return [new_x1, new_y1, new_x2, new_y2]
    
    def _point_in_bbox(self, point: Tuple[float, float], bbox: List[float]) -> bool:
        """Check if point is inside bounding box.
        
        Args:
            point: Point (x, y).
            bbox: Bounding box [x1, y1, x2, y2].
            
        Returns:
            True if point is inside.
        """
        x, y = point
        x1, y1, x2, y2 = bbox
        return x1 <= x <= x2 and y1 <= y <= y2
    
    def _calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Calculate IoU between two bounding boxes.
        
        Args:
            bbox1: First bounding box.
            bbox2: Second bounding box.
            
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
    
    def _calculate_intersection_over_phone_area(
        self,
        phone_bbox: List[float],
        person_bbox: List[float],
    ) -> float:
        """Calculate intersection over phone area.
        
        Args:
            phone_bbox: Phone bounding box.
            person_bbox: Person bounding box.
            
        Returns:
            Intersection over phone area ratio.
        """
        x1_1, y1_1, x2_1, y2_1 = phone_bbox
        x1_2, y1_2, x2_2, y2_2 = person_bbox
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Phone area
        phone_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        
        if phone_area == 0:
            return 0.0
        
        return intersection_area / phone_area
    
    def reset(self):
        """Reset temporal tracking state."""
        self._pending_switches.clear()
        logger.debug("Phone-student associator reset")
