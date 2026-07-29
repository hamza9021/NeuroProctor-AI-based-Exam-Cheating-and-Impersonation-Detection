"""6DRepNet head pose estimator."""

import logging
from typing import Tuple

import numpy as np
import torch

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    EVENT_INFERENCE_COMPLETED,
    EVENT_INFERENCE_STARTED,
)
from app.services.ai.analyzers.head_pose.exceptions import HeadPoseInferenceError
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class HeadPoseEstimator:
    """Runs 6DRepNet inference on face crops."""
    
    def __init__(
        self, model: torch.nn.Module, config: HeadPoseConfig, pipeline_logger: PipelineLogger
    ):
        """Initialize estimator.
        
        Args:
            model: Loaded 6DRepNet model.
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._model = model
        self._config = config
        self._logger = pipeline_logger
        self._device = next(model.parameters()).device
    
    async def estimate(self, crop: np.ndarray, track_id: int) -> Tuple[float, float, float]:
        """Estimate head pose from face crop.
        
        Args:
            crop: Face crop image.
            track_id: Track ID for logging.
            
        Returns:
            Raw model output (yaw, pitch, roll).
            
        Raises:
            HeadPoseInferenceError: If inference fails.
        """
        await self._logger.info(
            f"6DRepNet inference started for Track #{track_id}",
            emit_event=EVENT_INFERENCE_STARTED,
            data={"track_id": track_id},
        )
        
        try:
            # Preprocess crop
            tensor = self._preprocess(crop)
            
            # Run inference
            with torch.no_grad():
                output = self._model(tensor)
            
            await self._logger.info(
                f"6DRepNet inference completed for Track #{track_id}",
                emit_event=EVENT_INFERENCE_COMPLETED,
                data={"track_id": track_id},
            )
            
            # Convert to numpy and return
            return output.cpu().numpy().flatten()
            
        except Exception as e:
            logger.error(f"Inference failed for Track #{track_id}: {e}", exc_info=True)
            raise HeadPoseInferenceError(f"Inference failed: {e}")
    
    def _preprocess(self, crop: np.ndarray) -> torch.Tensor:
        """Preprocess face crop for 6DRepNet.
        
        Args:
            crop: Face crop image.
            
        Returns:
            Preprocessed tensor.
        """
        # Resize to expected input size from config
        import cv2
        resized = cv2.resize(crop, (self._config.input_size, self._config.input_size))
        
        # Convert to RGB if needed
        if len(resized.shape) == 3 and resized.shape[2] == 4:
            resized = resized[:, :, :3]
        
        # Normalize to [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        # Convert to tensor and add batch dimension
        tensor = torch.from_numpy(normalized).permute(2, 0, 1).unsqueeze(0)
        
        # Move to device
        tensor = tensor.to(self._device)
        
        logger.debug(
            "6DRepNet input tensor: shape=%s, device=%s, dtype=%s",
            tuple(tensor.shape),
            tensor.device,
            tensor.dtype,
        )
        
        return tensor
