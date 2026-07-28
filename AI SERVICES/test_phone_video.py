"""Test phone detection on a real video."""

import sys
from pathlib import Path
import cv2
import asyncio
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[0]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.ai.detectors.phone.config import PhoneDetectionConfig
from app.services.ai.detectors.phone.service import PhoneDetectionService
from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.pipeline.context import FrameContext
from app.config.settings import settings


async def test_phone_detection():
    """Test phone detection on a real video."""
    
    # Find a test video
    video_path = Path("temp/phone.mov")
    if not video_path.exists():
        print(f"Video not found: {video_path}")
        return
    
    print(f"Testing phone detection on: {video_path}")
    
    # Initialize configurations
    yolo_config = YOLOConfig(
        model_path=settings.YOLO_MODEL,
        confidence=settings.YOLO_CONFIDENCE,
        iou=settings.YOLO_IOU,
        image_size=settings.YOLO_IMAGE_SIZE,
        device=settings.YOLO_DEVICE,
    )
    
    phone_config = PhoneDetectionConfig(
        enabled=settings.PHONE_DETECTION_ENABLED,
        model_path=settings.PHONE_MODEL_PATH,
        class_name=settings.PHONE_CLASS_NAME,
        confidence=settings.PHONE_CONFIDENCE,
        image_size=settings.PHONE_IMAGE_SIZE,
        fallback_image_sizes=[int(x) for x in settings.PHONE_FALLBACK_IMAGE_SIZES.split(",")],
        min_box_area=settings.PHONE_MIN_BOX_AREA,
        roi_enabled=settings.PHONE_ROI_ENABLED,
        roi_expansion=settings.PHONE_ROI_EXPANSION,
        temporal_confirm_frames=settings.PHONE_TEMPORAL_CONFIRM_FRAMES,
        temporal_max_missed_frames=settings.PHONE_TEMPORAL_MAX_MISSED_FRAMES,
        association_iou=settings.PHONE_ASSOCIATION_IOU,
        deduplication_iou=settings.PHONE_DEDUPLICATION_IOU,
        debug_enabled=settings.PHONE_DEBUG_ENABLED,
        debug_max_frames=settings.PHONE_DEBUG_MAX_FRAMES,
    )
    
    # Initialize phone service
    phone_service = PhoneDetectionService(phone_config, yolo_config)
    phone_service.initialize()
    
    # Check if phone class ID was resolved
    print(f"Phone class ID resolved: {phone_service._phone_class_id}")
    if phone_service._phone_class_id is None:
        print("WARNING: Phone class ID not resolved - phone detection will not work")
        return
    
    # Check if raw debug mode is enabled
    raw_debug_mode = phone_config.debug_enabled
    print(f"Raw debug mode: {raw_debug_mode}")
    if raw_debug_mode:
        print(f"Raw debug confidence: {phone_config.raw_debug_confidence}")
        print(f"Raw debug image size: {phone_config.raw_debug_image_size}")
    
    # Open video
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {total_frames}")
    
    # Determine frame range
    start_frame = phone_config.test_start_frame
    end_frame = phone_config.test_end_frame if phone_config.test_end_frame > 0 else total_frames
    max_frames = phone_config.test_max_frames if phone_config.test_max_frames > 0 else (end_frame - start_frame)
    frame_step = phone_config.test_frame_step
    
    print(f"Frame range: {start_frame} to {end_frame} (step: {frame_step})")
    print(f"Max frames to process: {max_frames}")
    
    # Process frames
    frame_count = 0
    processed_count = 0
    total_phones_detected = 0
    
    while processed_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Skip frames before start
        if frame_count < start_frame:
            continue
        
        # Skip frames after end
        if frame_count > end_frame:
            break
        
        # Apply frame step
        if (frame_count - start_frame) % frame_step != 0:
            continue
        
        processed_count += 1
        
        # Create context
        context = FrameContext(
            frame=frame,
            frame_number=frame_count,
            timestamp=datetime.now(),
        )
        
        # Detect phones (without student tracks for simplicity)
        phone_tracks = phone_service.detect_phones(context, student_tracks=[], raw_debug_mode=raw_debug_mode)
        
        # Also check raw detections for debugging
        if frame_count <= 5:  # Only log first few frames
            print(f"Frame {frame_count}: Checking raw YOLO detections...")
            temp_context = FrameContext(frame=frame, frame_number=frame_count, timestamp=datetime.now())
            temp_context = phone_service._yolo_service.detect(temp_context)
            print(f"  Total YOLO detections: {len(temp_context.detections)}")
            for det in temp_context.detections:
                print(f"    - {det.class_name}: {det.confidence:.2f}, class_id={det.class_id}")
        
        # Log detection details
        if phone_tracks:
            total_phones_detected += len(phone_tracks)
            print(f"Frame {frame_count}: {len(phone_tracks)} phone detection(s)")
            for track in phone_tracks:
                state = track.state.value if hasattr(track.state, 'value') else str(track.state)
                print(f"  - Phone ID {track.phone_track_id}: state={state}, confidence={track.confidence:.2f}, "
                      f"bbox={track.bounding_box}, student={track.student_track_id}")
    
    cap.release()
    
    print(f"\nTest complete:")
    print(f"- Total frames in video: {total_frames}")
    print(f"- Frames processed: {processed_count}")
    print(f"- Total confirmed phone detections: {total_phones_detected}")
    print(f"- Average phones per processed frame: {total_phones_detected / processed_count if processed_count > 0 else 0:.2f}")


if __name__ == "__main__":
    asyncio.run(test_phone_detection())
