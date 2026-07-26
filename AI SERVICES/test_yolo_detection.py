"""Integration test for YOLO detection stage."""

import numpy as np
from datetime import datetime

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.stage import YOLODetectionStage
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.monitoring import PipelineLogger


def test_yolo_detection():
    """Test YOLO detection stage integration."""
    
    # Create configuration
    config = YOLOConfig(
        model_path="yolov8m.pt",  # Will be downloaded by ultralytics
        confidence=0.25,
        iou=0.45,
        image_size=640,
        device="auto",
    )
    
    # Create pipeline logger (for testing, use minimal logger)
    pipeline_logger = PipelineLogger(session_id="test-session")
    
    # Create YOLO stage
    stage = YOLODetectionStage(config, pipeline_logger)
    
    # Create test frame (640x640 RGB)
    test_frame = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    # Create frame context
    context = FrameContext(
        frame=test_frame,
        frame_number=1,
        timestamp=datetime.now(),
    )
    
    # Process frame through YOLO stage
    try:
        result_context = stage.process(context)
        
        # Verify detections exist
        assert result_context is not None
        assert hasattr(result_context, "detections")
        
        # Log results
        print(f"Frame processed successfully")
        print(f"Detections: {len(result_context.detections)}")
        
        for det in result_context.detections:
            print(f"  - {det.class_name} (conf: {det.confidence:.2f})")
        
        print("✓ YOLO detection test passed")
        return True
        
    except Exception as e:
        print(f"✗ YOLO detection test failed: {e}")
        return False


if __name__ == "__main__":
    test_yolo_detection()
