"""Device resolution utility for PyTorch models."""

import logging
import torch

logger = logging.getLogger(__name__)


def resolve_device(configured_device: str = "auto") -> str:
    """Resolve the appropriate device for PyTorch models.
    
    Args:
        configured_device: Device configuration ("auto", "cuda", "cpu", or "cuda:N").
    
    Returns:
        Resolved device string.
    """
    configured_device = configured_device.strip().lower()
    
    if configured_device == "auto":
        if torch.cuda.is_available():
            device = "cuda:0"
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"Configured AI device: auto")
            logger.info(f"CUDA available: True")
            logger.info(f"Selected AI device: {device}")
            logger.info(f"GPU: {gpu_name}")
        else:
            device = "cpu"
            logger.info(f"Configured AI device: auto")
            logger.info(f"CUDA available: False")
            logger.info(f"Selected AI device: cpu")
        return device
    
    if configured_device.startswith("cuda"):
        if not torch.cuda.is_available():
            logger.warning(
                "CUDA was requested but is unavailable. Falling back to CPU."
            )
            return "cpu"
        
        # Validate specific GPU index if provided
        if ":" in configured_device:
            try:
                gpu_index = int(configured_device.split(":")[1])
                if gpu_index >= torch.cuda.device_count():
                    logger.warning(
                        f"GPU index {gpu_index} is not available. "
                        f"Available GPUs: {torch.cuda.device_count()}. "
                        f"Falling back to cuda:0."
                    )
                    return "cuda:0"
            except (ValueError, IndexError):
                logger.warning(f"Invalid CUDA device format: {configured_device}. Using cuda:0")
                return "cuda:0"
        
        logger.info(f"Configured AI device: {configured_device}")
        logger.info(f"Selected AI device: {configured_device}")
        return configured_device
    
    # CPU or other device
    logger.info(f"Configured AI device: {configured_device}")
    logger.info(f"Selected AI device: {configured_device}")
    return configured_device
