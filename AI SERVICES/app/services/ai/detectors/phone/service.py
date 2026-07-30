"""Phone detection service with temporal tracking."""

import logging
from typing import List, Optional, Dict
from datetime import datetime
import numpy as np

from app.services.ai.detectors.phone.config import PhoneDetectionConfig
from app.services.ai.detectors.phone.temporal_tracker import PhoneTemporalTracker, PhoneTrack
from app.services.ai.detectors.yolo.service import YOLODetectionService
from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.common.device_resolver import resolve_device
from app.services.ai.pipeline.context import FrameContext, Detection
from app.services.ai.analyzers.phone.associator import PhoneStudentAssociator

logger = logging.getLogger(__name__)


class PhoneDetectionService:
    """Service for phone detection with temporal tracking."""
    
    def __init__(self, config: PhoneDetectionConfig, yolo_config: YOLOConfig):
        """Initialize phone detection service.
        
        Args:
            config: Phone detection configuration.
            yolo_config: YOLO configuration for fallback detection.
        """
        self._config = config
        self._yolo_config = yolo_config
        self._temporal_tracker = PhoneTemporalTracker(
            confirm_frames=config.temporal_confirm_frames,
            max_missed_frames=config.temporal_max_missed_frames,
        )
        self._associator = PhoneStudentAssociator(
            roi_expansion=config.roi_expansion,
            association_iou=config.association_iou,
            association_switch_confirm_frames=config.association_switch_confirm_frames,
            association_switch_margin=config.association_switch_margin,
            max_centre_distance=config.max_centre_distance,
            min_association_score=config.min_association_score,
        )
        self._yolo_service = None
        self._phone_model = None
        self._phone_class_id = None
        self._initialized = False
        self._current_image_size = config.image_size
        self._fallback_index = 0
        # Active phone usage events
        self._active_events: dict[tuple[int, int], dict] = {}
    
    def initialize(self):
        """Initialize phone detection service."""
        if not self._config.enabled:
            logger.info("Phone detection disabled in configuration")
            self._initialized = True
            return
        
        logger.info("=" * 60)
        logger.info("INITIALIZING PHONE DETECTION SERVICE")
        logger.info("=" * 60)
        logger.info(f"Phone detection enabled: {self._config.enabled}")
        logger.info(f"Configured phone model path: {self._config.model_path}")
        logger.info(f"Phone class name: {self._config.class_name}")
        logger.info(f"Configured phone confidence: {self._config.confidence}")
        logger.info(f"Configured phone image size: {self._config.image_size}")
        logger.info(f"Configured fallback image sizes: {self._config.fallback_image_sizes}")
        logger.info(f"Phone min box area: {self._config.min_box_area}")
        logger.info(f"ROI enabled: {self._config.roi_enabled}")
        logger.info(f"ROI expansion: {self._config.roi_expansion}")
        logger.info(f"Temporal confirm frames: {self._config.temporal_confirm_frames}")
        logger.info(f"Temporal max missed frames: {self._config.temporal_max_missed_frames}")
        logger.info(f"Association IoU: {self._config.association_iou}")
        logger.info(f"Deduplication IoU: {self._config.deduplication_iou}")
        logger.info(f"Debug enabled: {self._config.debug_enabled}")
        logger.info(f"Raw debug confidence: {self._config.raw_debug_confidence}")
        logger.info(f"Raw debug image size: {self._config.raw_debug_image_size}")
        
        # Resolve device
        device = resolve_device(self._yolo_config.device)
        logger.info(f"Configured device: {self._yolo_config.device}")
        logger.info(f"Resolved device: {device}")
        
        # Try to load dedicated phone model if configured
        if self._config.model_path:
            try:
                self._load_phone_model(device)
                logger.info(f"Using dedicated phone model: {self._config.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load dedicated phone model: {e}")
                logger.info("Falling back to main YOLO model for phone detection")
                self._use_yolo_fallback(device)
        else:
            logger.info("PHONE_MODEL_PATH is empty; using main YOLO model")
            self._use_yolo_fallback(device)
        
        # Log resolved class ID
        logger.info(f"Resolved phone class ID: {self._phone_class_id}")
        if self._phone_class_id is not None and hasattr(self._yolo_service, '_model'):
            logger.info(f"Model classes: {self._yolo_service._model.names}")
        
        self._initialized = True
        logger.info("Phone detection service initialized")
        logger.info("=" * 60)
    
    def _load_phone_model(self, device: str):
        """Load dedicated phone detection model.
        
        Args:
            device: Device to load model on.
        """
        from app.services.ai.detectors.yolo.loader import ModelLoader
        from app.services.ai.detectors.yolo.detector import Detector
        
        phone_config = YOLOConfig(
            model_path=self._config.model_path,
            confidence=self._config.confidence,
            iou=self._yolo_config.iou,
            image_size=self._config.image_size,
            device=device,
        )
        
        loader = ModelLoader(phone_config)
        self._phone_model = loader.load()
        self._phone_detector = Detector(self._phone_model, phone_config)
        
        # Resolve phone class ID from model
        if hasattr(self._phone_model, 'names'):
            self._phone_class_id = self._resolve_class_id(self._phone_model.names)
            if self._phone_class_id is None:
                logger.warning(f"Phone class '{self._config.class_name}' not found in model")
    
    def _use_yolo_fallback(self, device: str):
        """Use main YOLO model for phone detection.
        
        Args:
            device: Device to use.
        """
        self._yolo_service = YOLODetectionService(self._yolo_config)
        self._yolo_service.initialize()
        
        # Resolve phone class ID from YOLO model
        if hasattr(self._yolo_service._model, 'names'):
            self._phone_class_id = self._resolve_class_id(self._yolo_service._model.names)
            if self._phone_class_id is None:
                logger.warning(f"Phone class '{self._config.class_name}' not found in YOLO model")
    
    def _resolve_class_id(self, model_names: Dict[int, str]) -> Optional[int]:
        """Resolve phone class ID from model names.
        
        Args:
            model_names: Model class name mapping.
            
        Returns:
            Class ID or None if not found.
        """
        for class_id, class_name in model_names.items():
            if class_name.strip().lower() == self._config.class_name.lower():
                logger.info(f"Phone class ID resolved: {class_id} ({class_name})")
                return class_id
        return None
    
    def detect_phones(
        self,
        context: FrameContext,
        student_tracks: List = None,
        raw_debug_mode: bool = False,
    ) -> List[PhoneTrack]:
        """Detect phones in frame with temporal tracking.
        
        Args:
            context: Frame context with detections.
            student_tracks: List of student tracks for association.
            raw_debug_mode: If True, bypass temporal filtering and return raw detections.
            
        Returns:
            List of confirmed phone tracks or raw detections if debug mode.
        """
        if not self._config.enabled or not self._initialized:
            return []
        
        if self._phone_class_id is None:
            logger.debug("Phone class ID not resolved, skipping detection")
            return []
        
        try:
            # Use debug mode parameters if enabled
            if raw_debug_mode:
                confidence = self._config.raw_debug_confidence
                image_size = self._config.raw_debug_image_size
                logger.info(f"RAW DEBUG MODE: confidence={confidence}, image_size={image_size}")
            else:
                confidence = None
                image_size = None
            
            # Run phone detection
            phone_detections = self._run_detection(context.frame, confidence, image_size)
            logger.debug(f"Frame {context.frame_number}: Raw phone detections: {len(phone_detections)}")
            
            # Run ROI-based detection if enabled and student tracks available
            roi_detections = []
            if self._config.roi_enabled and student_tracks:
                roi_detections = self._run_roi_detection(context.frame, student_tracks, confidence, image_size)
                logger.debug(f"Frame {context.frame_number}: ROI phone detections: {len(roi_detections)}")
                # Merge ROI detections with full-frame detections
                phone_detections = self._merge_detections(phone_detections, roi_detections)
                logger.debug(f"Frame {context.frame_number}: Merged phone detections: {len(phone_detections)}")
            
            # Associate phones with students using the associator
            if student_tracks:
                frame_height, frame_width = context.frame.shape[:2]
                phone_detections = self._associator.associate(
                    phone_detections,
                    student_tracks,
                    frame_width,
                    frame_height,
                    context.frame_number,
                )
                logger.debug(f"Frame {context.frame_number}: Associated phone detections: {len(phone_detections)}")
            
            if raw_debug_mode:
                # Return raw detections as PhoneTrack objects for debugging
                debug_tracks = []
                for i, det in enumerate(phone_detections):
                    debug_track = PhoneTrack(
                        phone_track_id=i,
                        bounding_box=det["bbox"],
                        confidence=det["confidence"],
                        student_track_id=det.get("student_track_id"),
                        first_seen_frame=context.frame_number,
                        last_seen_frame=context.frame_number,
                        detection_count=1,
                        state=PhoneState.CANDIDATE,
                    )
                    debug_tracks.append(debug_track)
                logger.info(f"RAW DEBUG MODE: Returning {len(debug_tracks)} raw detections")
                return debug_tracks

            # Update temporal tracking
            confirmed_tracks = self._temporal_tracker.update(
                phone_detections,
                context.frame_number,
                student_tracks,
            )
            logger.debug(f"Frame {context.frame_number}: Confirmed phone tracks: {len(confirmed_tracks)}")
            
            # Generate phone usage events for confirmed tracks
            events = self._generate_phone_events(confirmed_tracks, context.frame_number, context.timestamp)
            if events:
                logger.info(f"Frame {context.frame_number}: Generated {len(events)} phone usage events")
                # Add events to context for downstream processing
                if not hasattr(context, 'events'):
                    context.events = []
                context.events.extend(events)
            
            return confirmed_tracks
            
        except Exception as e:
            logger.error(f"Phone detection failed: {e}", exc_info=True)
            return []
    
    def _run_detection(self, frame: np.ndarray, confidence: float = None, image_size: int = None) -> List[dict]:
        """Run phone detection on frame.
        
        Args:
            frame: Input frame.
            confidence: Override confidence threshold (for debug mode).
            image_size: Override image size (for debug mode).
            
        Returns:
            List of phone detections.
        """
        detections = []
        
        # Use provided values or config defaults
        conf_threshold = confidence if confidence is not None else self._config.confidence
        img_size = image_size if image_size is not None else self._current_image_size
        
        logger.debug(f"Running phone detection with confidence={conf_threshold}, image_size={img_size}")
        
        try:
            if self._phone_model is not None:
                # Use dedicated phone model with explicit parameters
                results = self._phone_model.predict(
                    source=frame,
                    conf=conf_threshold,
                    imgsz=img_size,
                    device=resolve_device(self._yolo_config.device),
                    verbose=False,
                )
                detections = self._parse_results(results)
            elif self._yolo_service is not None:
                # Use YOLO fallback - need to temporarily modify detector config
                # For now, use the existing approach but log the size
                logger.debug(f"Using YOLO fallback with image size {img_size}")
                temp_context = FrameContext(frame=frame, frame_number=0, timestamp=datetime.now())
                temp_context = self._yolo_service.detect(temp_context)
                detections = self._filter_phone_detections(temp_context.detections)
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                logger.warning(f"CUDA OOM at image size {img_size}, trying fallback")
                detections = self._try_fallback_detection(frame, conf_threshold)
            else:
                raise
        
        return detections
    
    def _try_fallback_detection(self, frame: np.ndarray, confidence: float = None) -> List[dict]:
        """Try detection with smaller image size.
        
        Args:
            frame: Input frame.
            confidence: Confidence threshold to use.
            
        Returns:
            List of phone detections.
        """
        if self._fallback_index >= len(self._config.fallback_image_sizes):
            logger.error("All fallback image sizes exhausted")
            return []
        
        fallback_size = self._config.fallback_image_sizes[self._fallback_index]
        self._fallback_index += 1
        logger.info(f"Retrying with image size: {fallback_size}")
        
        # Temporarily update image size
        original_size = self._current_image_size
        self._current_image_size = fallback_size
        
        conf_threshold = confidence if confidence is not None else self._config.confidence
        
        try:
            if self._phone_model is not None:
                # Reload detector with new size
                results = self._phone_model.predict(
                    source=frame,
                    conf=conf_threshold,
                    imgsz=fallback_size,
                    device=resolve_device(self._yolo_config.device),
                    verbose=False,
                )
                detections = self._parse_results(results)
            else:
                # Use YOLO fallback with smaller size
                temp_context = FrameContext(frame=frame, frame_number=0, timestamp=datetime.now())
                temp_context = self._yolo_service.detect(temp_context)
                detections = self._filter_phone_detections(temp_context.detections)
            
            # Reset fallback index on success
            self._fallback_index = 0
            self._current_image_size = original_size
            logger.info(f"Successfully detected with fallback size {fallback_size}")
            return detections
            
        except Exception as e:
            logger.error(f"Fallback detection failed: {e}")
            self._current_image_size = original_size
            return self._try_fallback_detection(frame, confidence)
    
    def _parse_results(self, results) -> List[dict]:
        """Parse detection results.
        
        Args:
            results: Raw detection results.
            
        Returns:
            List of detection dictionaries.
        """
        detections = []
        
        for result in results:
            if hasattr(result, 'boxes'):
                for box in result.boxes:
                    if box.cls[0] == self._phone_class_id:
                        detections.append({
                            "bbox": box.xyxy[0].tolist(),
                            "confidence": float(box.conf[0]),
                        })
        
        return detections
    
    def _filter_phone_detections(self, detections: List[Detection]) -> List[dict]:
        """Filter phone detections from YOLO results.
        
        Args:
            detections: All YOLO detections.
            
        Returns:
            List of phone detection dictionaries.
        """
        phone_detections = []
        
        for det in detections:
            if det.class_id == self._phone_class_id:
                phone_detections.append({
                    "bbox": det.bbox,
                    "confidence": det.confidence,
                })
        
        return phone_detections

    def _expand_bbox(self, bbox: List[float], expansion: float) -> List[float]:
        """Expand bounding box by factor.

        Args:
            bbox: Original bounding box.
            expansion: Expansion factor.

        Returns:
            Expanded bounding box.
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1

        x1_exp = x1 - width * expansion
        y1_exp = y1 - height * expansion
        x2_exp = x2 + width * expansion
        y2_exp = y2 + height * expansion

        return [x1_exp, y1_exp, x2_exp, y2_exp]

    def _point_in_bbox(self, point: List[float], bbox: List[float]) -> bool:
        """Check if point is inside bounding box.

        Args:
            point: Point coordinates [x, y].
            bbox: Bounding box [x1, y1, x2, y2].

        Returns:
            True if point is inside bbox.
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

    def _run_roi_detection(
        self,
        frame: np.ndarray,
        student_tracks: List,
        confidence: float = None,
        image_size: int = None,
    ) -> List[dict]:
        """Run phone detection in student ROIs.
        
        Args:
            frame: Input frame.
            student_tracks: List of student tracks.
            confidence: Confidence threshold.
            image_size: Image size for inference.
            
        Returns:
            List of phone detections with converted coordinates.
        """
        roi_detections = []
        
        for track in student_tracks:
            # Get student bounding box
            student_bbox = track.bbox
            
            # Expand ROI
            expanded_bbox = self._expand_bbox(student_bbox, self._config.roi_expansion)
            
            # Convert to integer coordinates
            x1, y1, x2, y2 = [int(coord) for coord in expanded_bbox]
            
            # Clip to frame boundaries
            height, width = frame.shape[:2]
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(width, x2)
            y2 = min(height, y2)
            
            # Skip if ROI is too small
            if x2 <= x1 or y2 <= y1:
                continue
            
            # Crop ROI
            roi = frame[y1:y2, x1:x2]
            
            # Run detection on ROI
            try:
                roi_dets = self._run_detection(roi, confidence, image_size)
                
                # Convert ROI-local coordinates to full-frame coordinates
                for det in roi_dets:
                    local_bbox = det["bbox"]
                    full_bbox = [
                        local_bbox[0] + x1,
                        local_bbox[1] + y1,
                        local_bbox[2] + x1,
                        local_bbox[3] + y1,
                    ]
                    det["bbox"] = full_bbox
                    det["student_track_id"] = track.track_id  # ROI source student
                    det["source_student_track_id"] = track.track_id  # Preserve ROI owner
                    roi_detections.append(det)
                    
            except Exception as e:
                logger.warning(f"ROI detection failed for student {track.track_id}: {e}")
        
        return roi_detections
    
    def _merge_detections(self, detections1: List[dict], detections2: List[dict]) -> List[dict]:
        """Merge two detection lists with deduplication.
        
        Args:
            detections1: First detection list.
            detections2: Second detection list.
            
        Returns:
            Merged and deduplicated detections.
        """
        merged = detections1.copy()
        
        for det2 in detections2:
            # Check if detection is duplicate
            is_duplicate = False
            for det1 in merged:
                iou = self._calculate_iou(det1["bbox"], det2["bbox"])
                if iou > self._config.deduplication_iou:
                    # Merge: keep the one with higher confidence and better association
                    keep_det1 = True
                    
                    # Prefer higher confidence
                    if det2["confidence"] > det1["confidence"]:
                        keep_det1 = False
                    # Prefer detection with reliable student association
                    elif det2.get("student_track_id") is not None and det1.get("student_track_id") is None:
                        keep_det1 = False
                    # Prefer ROI detection with valid track
                    elif det2.get("source_student_track_id") is not None and det1.get("source_student_track_id") is None:
                        keep_det1 = False
                    
                    if not keep_det1:
                        merged.remove(det1)
                        merged.append(det2)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged.append(det2)
        
        return merged
    
    def _generate_phone_events(self, confirmed_tracks: List[PhoneTrack], frame_number: int, timestamp: datetime) -> List[dict]:
        """Generate phone usage events for confirmed phone tracks.
        
        Args:
            confirmed_tracks: List of confirmed phone tracks.
            frame_number: Current frame number.
            timestamp: Current timestamp.
            
        Returns:
            List of phone usage events.
        """
        events = []
        events_to_remove = []
        
        for track in confirmed_tracks:
            # Only generate events for phones associated with students
            if track.student_track_id is None:
                continue
            
            event_key = (track.student_track_id, track.phone_track_id)
            
            # Check if this is a new or continuing event
            if event_key not in self._active_events:
                # New phone usage event
                event = {
                    "event_type": "phone_usage",
                    "student_track_id": track.student_track_id,
                    "phone_track_id": track.phone_track_id,
                    "confidence": track.confidence,
                    "bbox": track.bounding_box,
                    "frame_number": frame_number,
                    "timestamp": timestamp,
                    "association_score": track.association_score,
                    "association_method": track.association_method,
                    "start_frame": frame_number,
                    "start_timestamp": timestamp,
                }
                self._active_events[event_key] = event
                events.append(event)
                logger.info(f"New phone usage event: student {track.student_track_id}, phone {track.phone_track_id}")
            else:
                # Update existing event
                existing_event = self._active_events[event_key]
                existing_event["confidence"] = track.confidence
                existing_event["bbox"] = track.bounding_box
                existing_event["frame_number"] = frame_number
                existing_event["timestamp"] = timestamp
                existing_event["association_score"] = track.association_score
                existing_event["association_method"] = track.association_method
                existing_event["end_frame"] = frame_number
                existing_event["end_timestamp"] = timestamp
                # Don't add to events list - we only emit new events, not updates
        
        # Check for expired events (phones no longer confirmed or student changed)
        current_keys = {(track.student_track_id, track.phone_track_id) for track in confirmed_tracks if track.student_track_id is not None}
        
        for event_key in list(self._active_events.keys()):
            if event_key not in current_keys:
                # Event ended
                event = self._active_events[event_key]
                event["end_frame"] = frame_number
                event["end_timestamp"] = timestamp
                events.append(event)  # Emit the completed event
                events_to_remove.append(event_key)
                logger.info(f"Phone usage event ended: student {event_key[0]}, phone {event_key[1]}")
        
        # Remove expired events
        for key in events_to_remove:
            del self._active_events[key]
        
        return events
    
    def reset(self):
        """Reset temporal tracking state."""
        self._temporal_tracker.reset()
        self._fallback_index = 0
        logger.info("Phone detection service reset")
