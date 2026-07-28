"""Integration test for phone-to-student association with DeepSORT."""

import sys
from pathlib import Path
import cv2
from datetime import datetime
import asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[0]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import Settings
from app.services.ai.detectors.phone.config import PhoneDetectionConfig
from app.services.ai.detectors.phone.service import PhoneDetectionService
from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.service import YOLODetectionService
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.service import DeepSORTService
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.monitoring import PipelineLogger


async def main():
    """Run integration test for phone-student association."""
    print("=" * 80)
    print("PHONE-TO-STUDENT ASSOCIATION INTEGRATION TEST")
    print("=" * 80)
    
    # Load settings
    settings = Settings()
    print(f"\nConfiguration:")
    print(f"- Video path: temp/phone.mov")
    print(f"- Phone detection enabled: {settings.PHONE_DETECTION_ENABLED}")
    print(f"- Phone confidence: {settings.PHONE_CONFIDENCE}")
    print(f"- Phone image size: {settings.PHONE_IMAGE_SIZE}")
    print(f"- Association IoU: {settings.PHONE_ASSOCIATION_IOU}")
    print(f"- Association switch confirm frames: {settings.PHONE_ASSOCIATION_SWITCH_CONFIRM_FRAMES}")
    print(f"- Max centre distance: {settings.PHONE_MAX_CENTRE_DISTANCE}")
    print(f"- Min association score: {settings.PHONE_MIN_ASSOCIATION_SCORE}")
    
    # Initialize configurations
    yolo_config = YOLOConfig(
        model_path=settings.YOLO_MODEL,
        device="auto",
        confidence=settings.YOLO_CONFIDENCE,
        iou=settings.YOLO_IOU,
        image_size=settings.YOLO_IMAGE_SIZE,
    )
    
    deepsort_config = DeepSORTConfig(
        embedding_model="models/osx_x0_25",
        device="auto",
        max_iou_distance=0.7,
        max_cosine_distance=0.2,
        max_age=30,
        n_init=3,
        nn_budget=100,
        detection_confidence_threshold=0.3,
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
        raw_debug_confidence=settings.PHONE_RAW_DEBUG_CONFIDENCE,
        raw_debug_image_size=settings.PHONE_RAW_DEBUG_IMAGE_SIZE,
        test_max_frames=settings.PHONE_TEST_MAX_FRAMES,
        test_start_frame=settings.PHONE_TEST_START_FRAME,
        test_end_frame=settings.PHONE_TEST_END_FRAME,
        test_frame_step=settings.PHONE_TEST_FRAME_STEP,
        association_switch_confirm_frames=settings.PHONE_ASSOCIATION_SWITCH_CONFIRM_FRAMES,
        association_switch_margin=settings.PHONE_ASSOCIATION_SWITCH_MARGIN,
        max_centre_distance=settings.PHONE_MAX_CENTRE_DISTANCE,
        min_association_score=settings.PHONE_MIN_ASSOCIATION_SCORE,
    )
    
    # Initialize services
    print("\nInitializing services...")
    pipeline_logger = PipelineLogger(session_id="phone-association-test")
    
    yolo_service = YOLODetectionService(yolo_config)
    yolo_service.initialize()
    
    deepsort_service = DeepSORTService(deepsort_config, pipeline_logger)
    
    phone_service = PhoneDetectionService(phone_config, yolo_config)
    phone_service.initialize()
    
    # Open video
    video_path = Path("temp/phone.mov")
    if not video_path.exists():
        print(f"ERROR: Video not found at {video_path}")
        return
    
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"\nVideo info:")
    print(f"- Total frames: {total_frames}")
    print(f"- FPS: {fps}")
    print(f"- Resolution: {width}x{height}")
    
    # Setup output video
    output_path = Path("annotated_videos/phone_association_test.mp4")
    output_path.parent.mkdir(exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    # Process frames
    print("\nProcessing frames...")
    frame_count = 0
    association_report = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Apply frame range configuration
        if phone_config.test_start_frame > 0 and frame_count < phone_config.test_start_frame:
            continue
        if phone_config.test_end_frame > 0 and frame_count > phone_config.test_end_frame:
            continue
        if phone_config.test_frame_step > 1 and frame_count % phone_config.test_frame_step != 0:
            continue
        if phone_config.test_max_frames > 0 and (frame_count - phone_config.test_start_frame) > phone_config.test_max_frames:
            break
        
        # Run YOLO detection
        context = FrameContext(frame=frame, frame_number=frame_count, timestamp=datetime.now())
        context = yolo_service.detect(context)
        
        # Run DeepSORT tracking (async call)
        context = await deepsort_service.track(context)
        
        # Run phone detection with association
        phone_tracks = phone_service.detect_phones(context, context.tracks)
        
        # Draw annotations
        annotated = frame.copy()
        
        # Draw DeepSORT tracks
        for track in context.tracks:
            x1, y1, x2, y2 = [int(coord) for coord in track.bbox]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                f"Person {track.track_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
        
        # Draw phone detections with association info
        for phone_track in phone_tracks:
            x1, y1, x2, y2 = [int(coord) for coord in phone_track.bounding_box]
            
            # Color based on state
            if phone_track.state.value == "confirmed":
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 165, 255)  # Orange
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Label with student association
            student_id = phone_track.student_track_id if phone_track.student_track_id else "Unknown"
            label = f"Phone {phone_track.phone_track_id} | {phone_track.confidence:.2f} | Student {student_id}"
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
            
            # Report association
            if phone_track.state.value == "confirmed":
                association_report.append({
                    "frame_number": frame_count,
                    "phone_track_id": phone_track.phone_track_id,
                    "student_track_id": phone_track.student_track_id,
                    "phone_confidence": phone_track.confidence,
                    "association_score": phone_track.association_score,
                    "association_method": phone_track.association_method,
                })
        
        # Write frame
        writer.write(annotated)
        
        # Log progress
        if frame_count % 50 == 0:
            print(f"Processed {frame_count}/{total_frames} frames")
    
    cap.release()
    writer.release()
    
    # Print association report
    print("\n" + "=" * 80)
    print("ASSOCIATION REPORT")
    print("=" * 80)
    print(f"{'Frame':<8} {'Phone ID':<10} {'Student ID':<12} {'Confidence':<12} {'Score':<8} {'Method':<30}")
    print("-" * 80)
    
    for entry in association_report:
        student_id = entry["student_track_id"] if entry["student_track_id"] else "Unknown"
        print(
            f"{entry['frame_number']:<8} "
            f"{entry['phone_track_id']:<10} "
            f"{student_id:<12} "
            f"{entry['phone_confidence']:<12.2f} "
            f"{entry['association_score']:<8.2f} "
            f"{entry['association_method']:<30}"
        )
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total frames processed: {frame_count}")
    print(f"Total confirmed phone detections: {len(association_report)}")
    
    # Count associations
    associated = sum(1 for e in association_report if e["student_track_id"] is not None)
    unassociated = len(association_report) - associated
    print(f"Associated with students: {associated}")
    print(f"Unassociated (Unknown): {unassociated}")
    
    # Count by student
    student_counts = {}
    for entry in association_report:
        if entry["student_track_id"] is not None:
            student_counts[entry["student_track_id"]] = student_counts.get(entry["student_track_id"], 0) + 1
    
    if student_counts:
        print("\nPhone detections by student:")
        for student_id, count in sorted(student_counts.items()):
            print(f"  Student {student_id}: {count} detections")
    
    # Count by association method
    method_counts = {}
    for entry in association_report:
        method = entry["association_method"]
        method_counts[method] = method_counts.get(method, 0) + 1
    
    if method_counts:
        print("\nAssociation methods:")
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {method}: {count}")
    
    print(f"\nAnnotated video saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
