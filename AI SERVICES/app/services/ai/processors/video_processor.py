"""Video processor with YOLO detection and DeepSORT tracking."""

import cv2
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.stage import YOLODetectionStage
from app.services.ai.detectors.phone.config import PhoneDetectionConfig
from app.services.ai.detectors.phone.service import PhoneDetectionService
from app.services.ai.detectors.phone.temporal_tracker import PhoneState
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.processors.frame_extractor import FrameExtractor
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.stage import DeepSORTStage
from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.stage import YoloPoseStage
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.stage import SixDRepNetHeadPoseStage
from app.services.ai.monitoring import PipelineLogger, EventEmitter

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes video through YOLO detection and DeepSORT tracking pipeline."""
    
    def __init__(
        self,
        yolo_config: YOLOConfig,
        deepsort_config: DeepSORTConfig,
        pose_config: YoloPoseConfig,
        phone_config: PhoneDetectionConfig,
        head_pose_config: HeadPoseConfig,
        pipeline_logger: PipelineLogger,
    ):
        """Initialize video processor.
        
        Args:
            yolo_config: YOLO configuration.
            deepsort_config: DeepSORT configuration.
            pose_config: Pose configuration.
            phone_config: Phone detection configuration.
            head_pose_config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._yolo_config = yolo_config
        self._deepsort_config = deepsort_config
        self._pose_config = pose_config
        self._phone_config = phone_config
        self._head_pose_config = head_pose_config
        self._pipeline_logger = pipeline_logger
        self._event_emitter = EventEmitter(pipeline_logger)
        self._yolo_stage: Optional[YOLODetectionStage] = None
        self._deepsort_stage: Optional[DeepSORTStage] = None
        self._pose_stage: Optional[YoloPoseStage] = None
        self._head_pose_stage: Optional[SixDRepNetHeadPoseStage] = None
        self._phone_service: Optional[PhoneDetectionService] = None
    
    async def process_video(self, video_path: Path, output_path: Path) -> dict:
        """Process video through YOLO detection and DeepSORT tracking pipeline.
        
        Args:
            video_path: Path to input video.
            output_path: Path to output video (annotated).
            
        Returns:
            Processing statistics.
        """
        logger.info(f"Processing video: {video_path}")
        
        # Initialize stages
        if self._yolo_stage is None:
            self._yolo_stage = YOLODetectionStage(self._yolo_config, self._pipeline_logger)
        
        if self._deepsort_stage is None:
            self._deepsort_stage = DeepSORTStage(self._deepsort_config, self._pipeline_logger)
        
        if self._pose_stage is None:
            self._pose_stage = YoloPoseStage(self._pose_config, self._pipeline_logger)
        
        if self._head_pose_stage is None:
            self._head_pose_stage = SixDRepNetHeadPoseStage(self._head_pose_config, self._pipeline_logger)
        
        if self._phone_service is None:
            self._phone_service = PhoneDetectionService(self._phone_config, self._yolo_config)
            self._phone_service.initialize()
        
        # Extract frames and process
        extractor = FrameExtractor(video_path)
        total_frames = extractor.get_frame_count()
        
        logger.info(f"Total frames: {total_frames}")
        
        # Setup video writer for output
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        detection_stats = {}
        track_stats = {}
        
        for frame_number, frame in extractor.extract_frames():
            # Calculate progress percentage
            progress = int((frame_number / total_frames) * 100)
            
            # Emit progress event
            await self._event_emitter.emit_info(
                f"Processing frame {frame_number}/{total_frames} ({progress}%)",
                data={
                    "frame_number": frame_number,
                    "total_frames": total_frames,
                    "progress": progress,
                    "stage": "video_processing"
                }
            )
            
            # Create frame context
            context = FrameContext(
                frame=frame,
                frame_number=frame_number,
                timestamp=datetime.now(),
            )
            
            # Process through YOLO stage
            context = await self._yolo_stage.process(context)
            
            # Draw non-person YOLO detections before DeepSORT
            context.frame = self._draw_non_person_detections(context.frame, context.detections)
            
            # Process through DeepSORT stage
            context = await self._deepsort_stage.process(context)
            
            # Detect phones with temporal tracking
            phone_tracks = []
            if self._phone_service is not None:
                phone_tracks = self._phone_service.detect_phones(context, context.tracks)
            
            # Process through Pose stage
            context = await self._pose_stage.process(context)
            
            # Process through Head Pose stage
            context = await self._head_pose_stage.process(context)
            
            # Draw phone detections with debug mode
            debug_mode = self._phone_config.debug_enabled if self._phone_config else False
            context.frame = self._draw_phone_detections(
                frame=context.frame,
                phone_tracks=phone_tracks,
                debug_mode=debug_mode,
                frame_number=context.frame_number,
            )
            
            # Write annotated frame (DeepSORT annotates in-place)
            writer.write(context.frame)
            
            # Collect detection statistics
            for det in context.detections:
                class_name = det.class_name
                detection_stats[class_name] = detection_stats.get(class_name, 0) + 1
            
            # Collect track statistics
            for track in context.tracks:
                track_id = track.track_id
                track_stats[track_id] = track_stats.get(track_id, 0) + 1
        
        writer.release()
        extractor.close()
        
        logger.info(f"Video processing complete. Output: {output_path}")
        logger.info(f"Detection statistics: {detection_stats}")
        logger.info(f"Track statistics: {len(track_stats)} unique tracks")
        
        return {
            "total_frames": total_frames,
            "detections": detection_stats,
            "tracks": track_stats,
        }
    
    def _draw_phone_detections(self, frame, phone_tracks, debug_mode=False, frame_number=None):
        """Draw bounding boxes for confirmed phone detections.

        Args:
            frame: Input frame.
            phone_tracks: List of PhoneTrack objects.
            debug_mode: If True, draw candidate phones with different styling.
            frame_number: Current frame number for logging.

        Returns:
            Annotated frame with phone detection boxes.
        """
        annotated = frame.copy()

        for track in phone_tracks:
            x1, y1, x2, y2 = [int(coord) for coord in track.bounding_box]

            # End-to-end trace: PHONE ANNOTATOR
            logger.info(
                f"[PHONE ANNOTATOR] phone_track_id={track.phone_track_id}, "
                f"received_owner_track_id={track.student_track_id}, "
                f"type(received_owner_track_id)={type(track.student_track_id)}"
            )

            # Color based on state
            if track.state == PhoneState.CANDIDATE:
                color = (0, 165, 255)  # Orange for candidates
                line_thickness = 1
            elif track.state == PhoneState.CONFIRMED:
                color = (0, 255, 255)  # Yellow for confirmed
                line_thickness = 2
            else:
                color = (128, 128, 128)  # Gray for other states
                line_thickness = 1
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, line_thickness)
            
            # Draw label with state and student association
            state_label = track.state.value if hasattr(track.state, 'value') else str(track.state)
            student_id = track.student_track_id if track.student_track_id is not None else "Unknown"

            if debug_mode:
                label = f"Phone {state_label} | {track.confidence:.2f} | Student {student_id}"
            else:
                label = f"Cell Phone {track.confidence:.2f} | Student {student_id}"

            # Mandatory trace before drawing
            logger.info(
                "[PHONE RENDER] frame=%s phone_track_id=%s "
                "received_owner_track_id=%r owner_type=%s label=%r",
                frame_number if frame_number is not None else 'unknown',
                track.phone_track_id,
                track.student_track_id,
                type(track.student_track_id),
                label,
            )

            # End-to-end trace: PHONE ANNOTATOR (final label)
            logger.info(
                f"[PHONE ANNOTATOR] phone_track_id={track.phone_track_id}, "
                f"final_label='{label}'"
            )

            self._draw_label(annotated, label, (x1, y1), color)
            
            # Draw debug line to person centre if debug mode and student associated
            if debug_mode and track.student_track_id is not None and hasattr(track, 'association_method'):
                # Draw line from phone centre to show association
                phone_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                cv2.circle(annotated, phone_center, 3, color, -1)
        
        return annotated
    
    def _draw_non_person_detections(self, frame, detections):
        """Draw bounding boxes for non-person YOLO detections.
        
        Args:
            frame: Input frame.
            detections: List of Detection objects.
            
        Returns:
            Annotated frame with non-person detection boxes.
        """
        annotated = frame.copy()
        
        for det in detections:
            # Skip person detections (handled by DeepSORT)
            if det.class_name == "person":
                continue
            
            x1, y1, x2, y2 = [int(coord) for coord in det.bbox]
            
            # Get color for this class
            color = self._get_class_color(det.class_name)
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det.class_name} {det.confidence:.2f}"
            self._draw_label(annotated, label, (x1, y1), color)
        
        return annotated
    
    def _get_class_color(self, class_name: str) -> tuple:
        """Get color for detection class.
        
        Args:
            class_name: Detection class name.
            
        Returns:
            BGR color tuple.
        """
        colors = {
            "cell phone": (0, 255, 255),    # Yellow
            "laptop": (255, 0, 255),        # Magenta
            "book": (128, 0, 128),          # Purple
            "bottle": (0, 128, 255),        # Orange
        }
        return colors.get(class_name, (128, 128, 128))  # Default gray
    
    def _draw_label(self, frame, label: str, position: tuple, color: tuple):
        """Draw label on frame.
        
        Args:
            frame: Frame to draw on.
            label: Label text.
            position: Position (x, y).
            color: Color tuple.
        """
        x, y = position
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, thickness
        )
        
        cv2.rectangle(
            frame,
            (x, y - text_height - baseline - 5),
            (x + text_width + 10, y),
            color,
            -1,
        )
        
        cv2.putText(
            frame,
            label,
            (x + 5, y - baseline - 2),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
        )

