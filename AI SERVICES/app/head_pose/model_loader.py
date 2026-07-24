"""
6DRepNet Model Loader.

This module handles loading and initialization of the 6DRepNet head pose
estimation model with automatic device selection (CUDA/CPU).
"""

import torch
import numpy as np
from typing import Optional, Tuple
from pathlib import Path
import logging

from app.utils.logger import get_logger


class HeadPoseModelLoader:
    """
    Loader for 6DRepNet head pose estimation model.
    
    This class handles model initialization, device selection, and provides
    a clean interface for head pose inference.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        pretrained: bool = True,
    ):
        """
        Initialize the 6DRepNet model loader.
        
        Args:
            model_path: Path to model weights (if None, uses pretrained)
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
            pretrained: Whether to use pretrained weights
        """
        self.logger = get_logger(__name__)
        
        self.model_path = model_path
        self.device = self._select_device(device)
        self.pretrained = pretrained
        
        self.model = None
        self.is_loaded = False
        
        self._load_model()
    
    def _select_device(self, device: Optional[str]) -> str:
        """
        Select the appropriate device for inference.
        
        Args:
            device: User-specified device or None for auto-detection
            
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if device is not None:
            selected_device = device.lower()
            if selected_device == 'cuda' and not torch.cuda.is_available():
                self.logger.warning("CUDA requested but not available, falling back to CPU")
                return 'cpu'
            return selected_device
        
        # Force CPU to avoid device compatibility issues with 6DRepNet
        self.logger.info("Forcing CPU device for 6DRepNet to avoid compatibility issues")
        return 'cpu'
    
    def _load_model(self) -> None:
        """
        Load the 6DRepNet model.
        
        Raises:
            RuntimeError: If model loading fails
        """
        try:
            self.logger.info("Loading 6DRepNet head pose estimation model...")
            
            # Use local sixdrepnet package with fixed imports
            import sys
            import os
            # Add app directory to sys.path to import local sixdrepnet
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if app_dir not in sys.path:
                sys.path.insert(0, app_dir)
            
            # Import from local sixdrepnet package
            from app.sixdrepnet import SixDRepNet
            
            # Initialize model using the SixDRepNet_Detector API
            self.model = SixDRepNet(
                gpu_id=-1,  # Force CPU
                dict_path=self.model_path if self.model_path else ''
            )
            
            self.is_loaded = True
            self.logger.info("6DRepNet model loaded successfully")
            
            # Log model info
            self._log_model_info()
            
        except RuntimeError:
            raise
        except Exception as e:
            # Check if it's a download error and provide alternative
            error_msg = str(e)
            if "404" in error_msg or "Not Found" in error_msg:
                self.logger.error(f"Failed to load 6DRepNet model: {e}")
                self.logger.error("The default model download URL is not available.")
                self.logger.error("Alternative model download options:")
                self.logger.error("1. Download from HuggingFace:")
                self.logger.error("   https://huggingface.co/Cantina/head-pose-estimation/blob/main/6DRepNet_300W_LP_AFLW2000.pth")
                self.logger.error("2. Download from Google Drive:")
                self.logger.error("   https://drive.google.com/drive/folders/1V1pCV0BEW3mD-B9MogGrz_P91UhTtuE_?usp=sharing")
                self.logger.error("3. Place the downloaded model in: ~/.cache/torch/hub/checkpoints/")
                self.logger.error("   Or specify the path with model_path parameter")
            else:
                self.logger.error(f"Failed to load 6DRepNet model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def _log_model_info(self) -> None:
        """Log model information."""
        self.logger.info(f"Model device: {self.device}")
        self.logger.info(f"Model type: {type(self.model)}")
        # SixDRepNet_Detector doesn't expose .parameters() or standard PyTorch methods
        self.logger.info("SixDRepNet_Detector loaded successfully")
    
    def predict(
        self,
        face_crop: np.ndarray,
    ) -> Tuple[float, float, float]:
        """
        Predict head orientation from a face crop.
        
        Args:
            face_crop: Face crop as numpy array (H, W, 3) in RGB format
            
        Returns:
            Tuple of (yaw, pitch, roll) in degrees
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If face crop is invalid
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        try:
            # Validate face crop
            if face_crop is None:
                raise ValueError("Invalid face crop: None")
            
            if not isinstance(face_crop, np.ndarray):
                raise ValueError(f"Invalid face crop type: {type(face_crop)}, expected numpy.ndarray")
            
            if face_crop.size == 0:
                raise ValueError(f"Invalid face crop: empty array, shape: {face_crop.shape}")
            
            if len(face_crop.shape) != 3 or face_crop.shape[2] != 3:
                raise ValueError(f"Invalid face crop shape: {face_crop.shape}, expected (H, W, 3)")
            
            if face_crop.dtype != np.uint8:
                self.logger.warning(f"Face crop dtype: {face_crop.dtype}, expected uint8, converting")
                face_crop = face_crop.astype(np.uint8)
            
            # SixDRepNet_Detector.predict() expects raw BGR numpy array and handles preprocessing internally
            # It performs: BGR->RGB conversion, PIL conversion, transforms, normalization, tensor conversion
            pitch, yaw, roll = self.model.predict(face_crop)
            
            # The library returns (pitch, yaw, roll) as numpy arrays in degrees
            # Convert to float if they are arrays
            if isinstance(pitch, np.ndarray):
                pitch = float(pitch[0]) if len(pitch) > 0 else float(pitch)
            if isinstance(yaw, np.ndarray):
                yaw = float(yaw[0]) if len(yaw) > 0 else float(yaw)
            if isinstance(roll, np.ndarray):
                roll = float(roll[0]) if len(roll) > 0 else float(roll)
            
            return yaw, pitch, roll
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}")
    
    def get_device(self) -> str:
        """
        Get the current device.
        
        Returns:
            Device string
        """
        return self.device
    
    def is_model_loaded(self) -> bool:
        """
        Check if model is loaded.
        
        Returns:
            True if loaded, False otherwise
        """
        return self.is_loaded
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.model is not None:
            del self.model
            self.model = None
            self.is_loaded = False
        
        if self.device == 'cuda':
            torch.cuda.empty_cache()
        
        self.logger.info("6DRepNet model cleaned up")
