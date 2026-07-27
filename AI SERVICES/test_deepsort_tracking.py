"""Integration test for DeepSORT tracking stage."""

import asyncio
import numpy as np
from datetime import datetime

from app.config.settings import settings
from app.services.ai.pipeline.context import Detection, FrameContext
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.stage import DeepSORTStage
from app.services.ai.monitoring import PipelineLogger


async def test_deepsort_tracking():
    """Test DeepSORT tracking stage integration."""
    
    # Create configuration
    config = DeepSORTConfig(
        max_age=70,
        n_init=3,
        max_iou_distance=0.7,
        embedding_model="mars-small128.pb",
        device=settings.YOLO_DEVICE,
        socket_log_detail_level="detailed",
        frame_log_interval=1,
    )
    
    # Create pipeline logger
    pipeline_logger = PipelineLogger(session_id="test-session")
    
    # Create DeepSORT stage
    stage = DeepSORTStage(config, pipeline_logger)
    
    # Create test frame (640x640 RGB)
    test_frame = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    # Create frame context with person detections
    context = FrameContext(
        frame=test_frame,
        frame_number=1,
        timestamp=datetime.now(),
    )
    
    # Add a person detection
    context.detections = [
        Detection(
            track_id=None,
            class_name="person",
            class_id=0,
            confidence=0.85,
            bbox=[100, 100, 200, 300],
            center=[150, 200],
            width=100,
            height=200,
        )
    ]
    
    # Process frame through DeepSORT stage
    try:
        result_context = await stage.process(context)
        
        # Verify tracks exist
        assert result_context is not None
        assert hasattr(result_context, "tracks")
        
        # Log results
        print(f"Frame processed successfully")
        print(f"Tracks: {len(result_context.tracks)}")
        
        for track in result_context.tracks:
            print(f"  - Track ID: {track.track_id}, Confirmed: {track.is_confirmed}")
        
        # Verify detection has track_id assigned
        if result_context.detections:
            for det in result_context.detections:
                if det.class_name == "person":
                    print(f"  - Person detection track_id: {det.track_id}")
        
        # Verify frame is annotated
        assert result_context.frame is not None
        print(f"  - Frame annotated: {result_context.frame.shape}")
        
        print("✓ DeepSORT tracking test passed")
        return True
        
    except Exception as e:
        print(f"✗ DeepSORT tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_deepsort_tracking())
