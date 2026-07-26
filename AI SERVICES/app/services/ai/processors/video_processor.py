"""Video processor with YOLO detection."""

import cv2
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.stage import YOLODetectionStage
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.processors.frame_extractor import FrameExtractor
from app.services.ai.monitoring import PipelineLogger, EventEmitter

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes video through YOLO detection pipeline."""
    
    def __init__(self, yolo_config: YOLOConfig, pipeline_logger: PipelineLogger):
        """Initialize video processor.
        
        Args:
            yolo_config: YOLO configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._yolo_config = yolo_config
        self._pipeline_logger = pipeline_logger
        self._event_emitter = EventEmitter(pipeline_logger)
        self._yolo_stage: Optional[YOLODetectionStage] = None
    
    async def process_video(self, video_path: Path, output_path: Path) -> dict:
        """Process video through YOLO detection pipeline.
        
        Args:
            video_path: Path to input video.
            output_path: Path to output video (annotated).
            
        Returns:
            Processing statistics.
        """
        logger.info(f"Processing video: {video_path}")
        
        # Initialize YOLO stage
        if self._yolo_stage is None:
            self._yolo_stage = YOLODetectionStage(self._yolo_config, self._pipeline_logger)
        
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
                    "stage": "yolo_detection"
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
            
            # Draw detections on frame
            annotated_frame = self._draw_detections(frame, context.detections)
            
            # Write to output video
            writer.write(annotated_frame)
            
            # Collect statistics
            for det in context.detections:
                class_name = det.class_name
                detection_stats[class_name] = detection_stats.get(class_name, 0) + 1
        
        writer.release()
        extractor.close()
        
        logger.info(f"Video processing complete. Output: {output_path}")
        logger.info(f"Detection statistics: {detection_stats}")
        
        return {
            "total_frames": total_frames,
            "detections": detection_stats,
        }
    
    def _draw_detections(self, frame, detections) -> any:
        """Draw detection boxes on frame.
        
        Args:
            frame: Input frame.
            detections: List of Detection objects.
            
        Returns:
            Annotated frame.
        """
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = [int(coord) for coord in det.bbox]
            
            # Draw bounding box
            color = self._get_class_color(det.class_name)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det.class_name} {det.confidence:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return annotated
    
    def _get_class_color(self, class_name: str) -> tuple:
        """Get color for class name.
        
        Args:
            class_name: Class name.
            
        Returns:
            RGB color tuple.
        """
        colors = {
            "person": (0, 255, 0),
            "cell phone": (255, 0, 0),
            "book": (0, 0, 255),
            "laptop": (255, 255, 0),
            "tablet": (255, 0, 255),
            "mouse": (0, 255, 255),
            "keyboard": (128, 0, 128),
        }
        return colors.get(class_name, (255, 255, 255))
