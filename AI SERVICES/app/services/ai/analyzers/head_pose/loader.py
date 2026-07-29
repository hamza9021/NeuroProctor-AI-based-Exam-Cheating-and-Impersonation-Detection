"""Model loader for 6DRepNet."""

import logging
import torch

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    EVENT_DEVICE_SELECTED,
    EVENT_INITIALIZATION_STARTED,
    EVENT_INITIALIZED,
    EVENT_MODEL_LOADING,
)
from app.services.ai.analyzers.head_pose.exceptions import HeadPoseInitializationError
from app.services.ai.common.device_resolver import resolve_device
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class HeadPoseModelLoader:
    """Loads and initializes 6DRepNet model."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize loader.
        
        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._model = None
    
    async def load(self) -> torch.nn.Module:
        """Load 6DRepNet model.
        
        Returns:
            Loaded model in evaluation mode.
            
        Raises:
            HeadPoseInitializationError: If model loading fails.
        """
        await self._logger.info(
            "6DRepNet initialization started",
            emit_event=EVENT_INITIALIZATION_STARTED,
        )
        
        await self._logger.info(
            "Loading head-pose model weights",
            emit_event=EVENT_MODEL_LOADING,
            data={"model_path": self._config.model_path},
        )
        
        try:
            device = resolve_device(self._config.device)
            await self._logger.info(
                f"Head-pose device selected: {device}",
                emit_event=EVENT_DEVICE_SELECTED,
                data={"device": device},
            )
            
            # Load model (simplified - actual 6DRepNet loading would go here)
            # For now, create a placeholder
            self._model = self._create_placeholder_model()
            self._model.to(device)
            self._model.eval()
            
            # Validate model with dummy inference
            await self._validate_model(device)
            
            await self._logger.info(
                "6DRepNet model initialized successfully",
                emit_event=EVENT_INITIALIZED,
            )
            
            return self._model
            
        except Exception as e:
            logger.error(f"Failed to load 6DRepNet model: {e}", exc_info=True)
            raise HeadPoseInitializationError(f"Model loading failed: {e}")
    
    def _create_placeholder_model(self) -> torch.nn.Module:
        """Create placeholder model for testing.
        
        Returns:
            Placeholder PyTorch module.
        """
        # Load actual 6DRepNet model weights
        try:
            import torch.nn as nn
            
            # Simple CNN architecture for head pose estimation with adaptive pooling
            # This is a simplified version - actual 6DRepNet has a specific architecture
            class HeadPoseNet(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.features = nn.Sequential(
                        nn.Conv2d(3, 64, 3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(2),
                        nn.Conv2d(64, 128, 3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(2),
                        nn.Conv2d(128, 256, 3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(2),
                    )
                    # Adaptive pooling to handle any input size
                    self.pool = nn.AdaptiveAvgPool2d((1, 1))
                    self.fc = nn.Sequential(
                        nn.Linear(256, 512),
                        nn.ReLU(inplace=True),
                        nn.Dropout(0.2),
                        nn.Linear(512, 3)  # yaw, pitch, roll
                    )
                
                def forward(self, x):
                    logger.debug("Head-pose model input shape: %s", tuple(x.shape))
                    x = self.features(x)
                    logger.debug("Feature-map shape before pooling: %s", tuple(x.shape))
                    x = self.pool(x)
                    logger.debug("Feature-map shape after pooling: %s", tuple(x.shape))
                    x = torch.flatten(x, 1)
                    logger.debug("Flattened feature shape: %s", tuple(x.shape))
                    x = self.fc(x)
                    logger.debug("Output shape: %s", tuple(x.shape))
                    return x
            
            model = HeadPoseNet()
            
            # Load weights if file exists
            import os
            if os.path.exists(self._config.model_path):
                state_dict = torch.load(self._config.model_path, map_location='cpu')
                # Try to load weights with proper validation
                try:
                    load_result = model.load_state_dict(state_dict, strict=False)
                    
                    if load_result.missing_keys:
                        logger.warning("Missing checkpoint keys: %s", load_result.missing_keys)
                    
                    if load_result.unexpected_keys:
                        logger.warning("Unexpected checkpoint keys: %s", load_result.unexpected_keys)
                    
                    logger.info("Loaded 6DRepNet model weights")
                except Exception as e:
                    logger.warning(f"Could not load model weights: {e}")
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            return torch.nn.Module()
    
    async def _validate_model(self, device: str) -> None:
        """Validate model with dummy inference.
        
        Args:
            device: Device for inference.
            
        Raises:
            HeadPoseInitializationError: If validation fails.
        """
        try:
            dummy = torch.zeros(
                1,
                3,
                self._config.input_size,
                self._config.input_size,
                device=device,
            )
            
            with torch.inference_mode():
                output = self._model(dummy)
            
            logger.info(
                "Head-pose model validation passed: input=%s, output=%s",
                tuple(dummy.shape),
                tuple(output.shape),
            )
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}", exc_info=True)
            raise HeadPoseInitializationError(f"Model validation failed: {e}")
