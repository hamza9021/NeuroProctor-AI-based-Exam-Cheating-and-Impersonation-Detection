"""Video processor with YOLO detection and DeepSORT tracking."""

import cv2
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.stage import YOLODetectionStage
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.processors.frame_extractor import FrameExtractor
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.stage import DeepSORTStage
from app.services.ai.monitoring import PipelineLogger, EventEmitter

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes video through YOLO detection and DeepSORT tracking pipeline."""
    
    def __init__(
        self,
        yolo_config: YOLOConfig,
        deepsort_config: DeepSORTConfig,
        pipeline_logger: PipelineLogger,
    ):
        """Initialize video processor.
        
        Args:
            yolo_config: YOLO configuration.
            deepsort_config: DeepSORT configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._yolo_config = yolo_config
        self._deepsort_config = deepsort_config
        self._pipeline_logger = pipeline_logger
        self._event_emitter = EventEmitter(pipeline_logger)
        self._yolo_stage: Optional[YOLODetectionStage] = None
        self._deepsort_stage: Optional[DeepSORTStage] = None
    
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
            
            # Process through DeepSORT stage
            context = await self._deepsort_stage.process(context)
            
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

