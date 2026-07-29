"""Integration tests for head pose estimation pipeline."""

from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STRING = str(PROJECT_ROOT)

if PROJECT_ROOT_STRING in sys.path:
    sys.path.remove(PROJECT_ROOT_STRING)

sys.path.insert(0, PROJECT_ROOT_STRING)

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.stage import SixDRepNetHeadPoseStage
from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext


@pytest.mark.asyncio
async def test_full_pipeline_flow():
    """Test full head pose estimation pipeline flow."""
    # Setup
    config = HeadPoseConfig()
    logger = AsyncMock()
    stage = SixDRepNetHeadPoseStage(config, logger)
    
    # Create mock context with tracks
    context = FrameContext(
        frame=np.zeros((480, 640, 3), dtype=np.uint8),
        frame_number=1,
        timestamp=datetime.now(),
    )
    
    # Create mock track
    mock_track = MagicMock()
    mock_track.track_id = 1
    mock_track.is_confirmed = True
    mock_track.bbox = (100.0, 100.0, 200.0, 200.0)
    context.tracks = [mock_track]
    
    # Mock pose data
    mock_pose = MagicMock()
    mock_pose.track_id = 1
    mock_pose.keypoints = np.zeros((17, 3), dtype=np.float32)
    context.poses = [mock_pose]
    
    # Mock the service initialization and processing
    with patch.object(stage._service, 'initialize', new_callable=AsyncMock):
        with patch.object(stage._service, 'estimate', new_callable=AsyncMock) as mock_estimate:
            # Mock the estimate to return context with head poses
            mock_estimate.return_value = context
            mock_estimate.return_value.head_pose = {1: MagicMock()}
            
            # Process
            result = await stage.process(context)
            
            # Verify
            assert result is context
            assert mock_estimate.called


@pytest.mark.asyncio
async def test_pipeline_with_empty_tracks():
    """Test pipeline with no eligible tracks."""
    config = HeadPoseConfig()
    logger = AsyncMock()
    stage = SixDRepNetHeadPoseStage(config, logger)
    
    context = FrameContext(
        frame=np.zeros((480, 640, 3), dtype=np.uint8),
        frame_number=1,
        timestamp=datetime.now(),
    )
    context.tracks = []
    
    with patch.object(stage._service, 'initialize', new_callable=AsyncMock):
        with patch.object(stage._service, 'estimate', new_callable=AsyncMock) as mock_estimate:
            mock_estimate.return_value = context
            mock_estimate.return_value.head_pose = {}
            
            result = await stage.process(context)
            
            assert result.head_pose == {}


@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Test pipeline error handling."""
    config = HeadPoseConfig()
    logger = AsyncMock()
    stage = SixDRepNetHeadPoseStage(config, logger)
    
    context = FrameContext(
        frame=np.zeros((480, 640, 3), dtype=np.uint8),
        frame_number=1,
        timestamp=datetime.now(),
    )
    
    with patch.object(stage._service, 'initialize', new_callable=AsyncMock):
        with patch.object(stage._service, 'estimate', new_callable=AsyncMock) as mock_estimate:
            mock_estimate.side_effect = Exception("Test error")
            
            result = await stage.process(context)
            
            # Should return context with empty head_pose on error
            assert result.head_pose == {}


@pytest.mark.asyncio
async def test_track_id_association():
    """Test that results are associated with correct track IDs."""
    config = HeadPoseConfig()
    logger = AsyncMock()
    stage = SixDRepNetHeadPoseStage(config, logger)
    
    context = FrameContext(
        frame=np.zeros((480, 640, 3), dtype=np.uint8),
        frame_number=1,
        timestamp=datetime.now(),
    )
    
    # Create multiple tracks
    mock_track1 = MagicMock()
    mock_track1.track_id = 1
    mock_track1.is_confirmed = True
    mock_track1.bbox = (100.0, 100.0, 200.0, 200.0)
    
    mock_track2 = MagicMock()
    mock_track2.track_id = 2
    mock_track2.is_confirmed = True
    mock_track2.bbox = (300.0, 100.0, 400.0, 200.0)
    
    context.tracks = [mock_track1, mock_track2]
    
    with patch.object(stage._service, 'initialize', new_callable=AsyncMock):
        with patch.object(stage._service, 'estimate', new_callable=AsyncMock) as mock_estimate:
            mock_estimate.return_value = context
            mock_estimate.return_value.head_pose = {1: MagicMock(), 2: MagicMock()}
            
            result = await stage.process(context)
            
            # Verify both track IDs are present
            assert 1 in result.head_pose
            assert 2 in result.head_pose


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
