"""Integration test for YOLO pose estimation stage."""

import asyncio
import numpy as np
from datetime import datetime

from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.pose import PoseResult
from app.services.ai.analyzers.pose.service import YoloPoseService
from app.services.ai.analyzers.pose.stage import YoloPoseStage
from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext, Detection
from app.services.ai.trackers.deepsort.track import Track


async def test_pose_estimation():
    """Test pose estimation integration."""
    print("Testing YOLO pose estimation integration...")
    
    # Initialize configuration
    config = YoloPoseConfig(
        model_path="yolo11n-pose.pt",
        device="cpu",
        confidence=0.25,
        keypoint_confidence=0.25,
        track_iou_threshold=0.30,
    )
    
    # Initialize pipeline logger
    pipeline_logger = PipelineLogger(session_id="test-pose")
    
    # Initialize pose stage
    stage = YoloPoseStage(config, pipeline_logger)
    
    # Create test frame
    frame = np.zeros((640, 640, 3), dtype=np.uint8)
    
    # Create test tracks
    tracks = [
        Track(
            track_id=0,
            bbox=(100, 100, 200, 300),
            center=(150, 200),
            confidence=0.9,
            is_confirmed=True,
            age=5,
            hits=5,
            time_since_update=0,
            class_name="person",
        ),
    ]
    
    # Create frame context
    context = FrameContext(
        frame=frame,
        frame_number=1,
        timestamp=datetime.now(),
        tracks=tracks,
    )
    
    try:
        # Process through pose stage
        result_context = await stage.process(context)
        
        # Verify results
        assert hasattr(result_context, "poses"), "Context should have poses field"
        assert isinstance(result_context.poses, dict), "Poses should be a dictionary"
        
        print("✓ Pose estimation integration test passed")
        print(f"  - Poses stored: {len(result_context.poses)}")
        print(f"  - Frame annotated: {result_context.frame.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ Pose estimation integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_pose_estimation())
    exit(0 if success else 1)
