"""Unit tests for head pose estimation modules."""

from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STRING = str(PROJECT_ROOT)

if PROJECT_ROOT_STRING in sys.path:
    sys.path.remove(PROJECT_ROOT_STRING)

sys.path.insert(0, PROJECT_ROOT_STRING)

import app

print(f"Project root: {PROJECT_ROOT}")
print(f"Imported app from: {app.__file__}")

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    AXIS_PITCH,
    AXIS_ROLL,
    AXIS_YAW,
    VALID_ANGLES,
)
from app.services.ai.analyzers.head_pose.exceptions import (
    FaceRegionNotFoundError,
    HeadPoseInitializationError,
    HeadPoseParsingError,
    HeadPoseValidationError,
    InvalidFaceCropError,
)
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult
from app.services.ai.analyzers.head_pose.mapper import HeadPoseMapper
from app.services.ai.analyzers.head_pose.parser import HeadPoseParser
from app.services.ai.analyzers.head_pose.validator import HeadPoseValidator
from app.services.ai.pipeline.context import FrameContext


class TestHeadPoseConfig:
    """Test HeadPoseConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = HeadPoseConfig()
        assert config.model_path == "models/6drepnet/6DRepNet_300W_LP_AFLW2000.pth"
        assert config.device == "auto"
        assert config.face_padding == 0.20
        assert config.min_face_size == 40
        assert config.max_abs_angle == 90.0
        assert config.annotation_enabled is True
        assert config.draw_axis is True
        assert config.log_level == "detailed"
        assert config.frame_log_interval == 10
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = HeadPoseConfig(
            model_path="custom/path.pth",
            device="cuda",
            face_padding=0.30,
            min_face_size=50,
        )
        assert config.model_path == "custom/path.pth"
        assert config.device == "cuda"
        assert config.face_padding == 0.30
        assert config.min_face_size == 50


class TestHeadPoseResult:
    """Test HeadPoseResult dataclass."""
    
    def test_head_pose_result_creation(self):
        """Test creating a head pose result."""
        result = HeadPoseResult(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
            confidence=0.95,
            is_valid=True,
        )
        assert result.track_id == 1
        assert result.face_bbox == (10.0, 20.0, 30.0, 40.0)
        assert result.yaw == -15.5
        assert result.pitch == 8.2
        assert result.roll == 3.1
        assert result.confidence == 0.95
        assert result.is_valid is True
    
    def test_head_pose_result_defaults(self):
        """Test head pose result with default values."""
        result = HeadPoseResult(
            track_id=2,
            face_bbox=(0.0, 0.0, 50.0, 50.0),
            yaw=0.0,
            pitch=0.0,
            roll=0.0,
        )
        assert result.confidence is None
        assert result.is_valid is True


class TestHeadPoseParser:
    """Test HeadPoseParser."""
    
    @pytest.mark.asyncio
    async def test_parse_valid_output(self):
        """Test parsing valid model output."""
        logger = AsyncMock()
        parser = HeadPoseParser(logger)
        
        # Simulate 6DRepNet output: [pitch, yaw, roll] in radians
        raw_output = np.array([0.1, -0.4, 0.05])  # radians
        
        yaw, pitch, roll = await parser.parse(raw_output, track_id=1)
        
        # Check conversion to degrees
        assert isinstance(yaw, float)
        assert isinstance(pitch, float)
        assert isinstance(roll, float)
        assert abs(yaw - np.degrees(-0.4)) < 0.01
        assert abs(pitch - np.degrees(0.1)) < 0.01
        assert abs(roll - np.degrees(0.05)) < 0.01
    
    @pytest.mark.asyncio
    async def test_parse_invalid_output(self):
        """Test parsing invalid model output."""
        logger = AsyncMock()
        parser = HeadPoseParser(logger)
        
        # Invalid output shape
        raw_output = np.array([0.1, 0.2])  # Only 2 values
        
        with pytest.raises(HeadPoseParsingError):
            await parser.parse(raw_output, track_id=1)


class TestHeadPoseValidator:
    """Test HeadPoseValidator."""
    
    @pytest.mark.asyncio
    async def test_validate_valid_result(self):
        """Test validating a valid head pose result."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)
        
        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
        )
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_invalid_yaw(self):
        """Test validating with invalid yaw (exceeds limit)."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)
        
        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=100.0,  # Exceeds max_abs_angle
            pitch=8.2,
            roll=3.1,
        )
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_nan_value(self):
        """Test validating with NaN value."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)
        
        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=float('nan'),
            pitch=8.2,
            roll=3.1,
        )
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_invalid_bbox(self):
        """Test validating with invalid bounding box."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)
        
        is_valid = await validator.validate(
            track_id=1,
            face_bbox=(30.0, 20.0, 10.0, 40.0),  # x2 < x1
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
        )
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_negative_track_id(self):
        """Test validating with negative track ID."""
        logger = AsyncMock()
        config = HeadPoseConfig(max_abs_angle=90.0)
        validator = HeadPoseValidator(config, logger)
        
        is_valid = await validator.validate(
            track_id=-1,  # Invalid
            face_bbox=(10.0, 20.0, 30.0, 40.0),
            yaw=-15.5,
            pitch=8.2,
            roll=3.1,
        )
        
        assert is_valid is False


class TestHeadPoseMapper:
    """Test HeadPoseMapper."""
    
    @pytest.mark.asyncio
    async def test_map_results_to_context(self):
        """Test mapping head pose results to FrameContext."""
        logger = AsyncMock()
        mapper = HeadPoseMapper(logger)
        context = FrameContext(
            frame=np.zeros((480, 640, 3), dtype=np.uint8),
            frame_number=1,
            timestamp=datetime.now(),
        )
        
        results = [
            HeadPoseResult(
                track_id=1,
                face_bbox=(10.0, 20.0, 30.0, 40.0),
                yaw=-15.5,
                pitch=8.2,
                roll=3.1,
                is_valid=True,
            ),
            HeadPoseResult(
                track_id=2,
                face_bbox=(50.0, 60.0, 70.0, 80.0),
                yaw=10.0,
                pitch=-5.0,
                roll=2.0,
                is_valid=True,
            ),
        ]
        
        context = await mapper.map(context, results)
        
        assert context.head_pose is not None
        assert len(context.head_pose) == 2
        assert 1 in context.head_pose
        assert 2 in context.head_pose
        assert context.head_pose[1].track_id == 1
        assert context.head_pose[2].track_id == 2
    
    @pytest.mark.asyncio
    async def test_map_invalid_results(self):
        """Test mapping with invalid results (should be excluded)."""
        logger = AsyncMock()
        mapper = HeadPoseMapper(logger)
        context = FrameContext(
            frame=np.zeros((480, 640, 3), dtype=np.uint8),
            frame_number=1,
            timestamp=datetime.now(),
        )
        
        results = [
            HeadPoseResult(
                track_id=1,
                face_bbox=(10.0, 20.0, 30.0, 40.0),
                yaw=-15.5,
                pitch=8.2,
                roll=3.1,
                is_valid=True,
            ),
            HeadPoseResult(
                track_id=2,
                face_bbox=(50.0, 60.0, 70.0, 80.0),
                yaw=10.0,
                pitch=-5.0,
                roll=2.0,
                is_valid=False,  # Invalid
            ),
        ]
        
        context = await mapper.map(context, results)
        
        assert len(context.head_pose) == 1
        assert 1 in context.head_pose
        assert 2 not in context.head_pose


class TestConstants:
    """Test constants."""
    
    def test_valid_angles(self):
        """Test valid angle names."""
        assert AXIS_YAW in VALID_ANGLES
        assert AXIS_PITCH in VALID_ANGLES
        assert AXIS_ROLL in VALID_ANGLES
        assert len(VALID_ANGLES) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
