"""6DRepNet head-pose estimator.

Returns a 3x3 rotation matrix per face crop, as produced by the official
SixDRepNet forward method.  Angle conversion is performed downstream in
``HeadPoseParser``.
"""

import logging
import zlib
from typing import Optional

import cv2
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

# ImageNet statistics used by the official 6DRepNet preprocessing pipeline.
_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class HeadPoseEstimator:
    """Runs 6DRepNet inference on face crops.

    Each call to :meth:`estimate` performs a fresh forward pass and increments
    the internal inference counter.  No result caching or memoisation exists.

    The model is expected to receive the exact same preprocessing that the
    official SixDRepNet test pipeline applies:

    1. BGR → RGB conversion (OpenCV images are BGR).
    2. Resize + centre-crop to ``config.input_size`` × ``config.input_size``.
    3. float32 normalisation to [0, 1].
    4. ImageNet mean/std normalisation.
    5. Batch-dimension insertion.
    6. Transfer to inference device.

    Returns:
        numpy.ndarray of shape ``(3, 3)`` — the rotation matrix for the face
        crop.  **Not** a flat Euler-angle vector.  Conversion to pitch/yaw/roll
        is performed by :class:`HeadPoseParser`.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        config: HeadPoseConfig,
        pipeline_logger: PipelineLogger,
    ):
        """Initialise the estimator.

        Args:
            model: Loaded SixDRepNet model in evaluation mode.
            config: Head pose configuration (``input_size``, debug flags, …).
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._model = model
        self._config = config
        self._logger = pipeline_logger
        self._device: torch.device = next(model.parameters()).device
        self._inference_call_count: int = 0

    @property
    def inference_call_count(self) -> int:
        """Total number of inference calls made since instantiation."""
        return self._inference_call_count

    async def estimate(self, crop: np.ndarray, track_id: int) -> np.ndarray:
        """Run a fresh 6DRepNet forward pass on *crop*.

        Args:
            crop: Face crop as a BGR uint8 numpy array with shape ``(H, W, 3)``.
                  Must be a contiguous, independently owned array (use
                  ``FaceCropper.crop()`` which calls ``.copy()``).
            track_id: DeepSORT track ID — used only for logging.

        Returns:
            numpy.ndarray of shape ``(3, 3)``: the rotation matrix produced by
            SixDRepNet for this crop.  Raw values; no angle conversion.

        Raises:
            HeadPoseInferenceError: If preprocessing or the forward pass fail.
        """
        await self._logger.info(
            f"6DRepNet inference started for Track #{track_id}",
            emit_event=EVENT_INFERENCE_STARTED,
            data={"track_id": track_id},
        )

        try:
            # ---------------------------------------------------------------- #
            # Preprocess                                                        #
            # ---------------------------------------------------------------- #
            tensor = self._preprocess(crop)

            # ---------------------------------------------------------------- #
            # Forward pass                                                      #
            # ---------------------------------------------------------------- #
            with torch.inference_mode():
                output = self._model(tensor)  # shape: (1, 3, 3)

            self._inference_call_count += 1

            await self._logger.info(
                f"6DRepNet inference completed for Track #{track_id}",
                emit_event=EVENT_INFERENCE_COMPLETED,
                data={
                    "track_id": track_id,
                    "inference_call_count": self._inference_call_count,
                },
            )

            # ---------------------------------------------------------------- #
            # Extract rotation matrix — shape (3, 3)                           #
            # ---------------------------------------------------------------- #
            rot_matrix: np.ndarray = output[0].cpu().numpy()  # squeeze batch dim

            # ---------------------------------------------------------------- #
            # Diagnostic logging (gated)                                       #
            # ---------------------------------------------------------------- #
            logger.debug(
                "RAW rotation matrix  track_id=%d  call_count=%d  "
                "shape=%s  det=%.4f",
                track_id,
                self._inference_call_count,
                rot_matrix.shape,
                float(np.linalg.det(rot_matrix)),
            )

            if self._config.debug_tensor_checksums:
                flat = tensor.cpu().numpy().flatten().astype(np.float32)
                crc = zlib.crc32(flat.tobytes()) & 0xFFFF_FFFF
                logger.debug(
                    "[TENSOR STATS]  track_id=%d  shape=%s  "
                    "min=%.4f  max=%.4f  mean=%.4f  std=%.4f  crc32=%d",
                    track_id,
                    tuple(tensor.shape),
                    float(flat.min()),
                    float(flat.max()),
                    float(flat.mean()),
                    float(flat.std()),
                    crc,
                )

            return rot_matrix

        except HeadPoseInferenceError:
            raise
        except Exception as exc:
            logger.error(
                "Inference failed for Track #%d: %s", track_id, exc, exc_info=True
            )
            raise HeadPoseInferenceError(f"Inference failed: {exc}") from exc

    # ---------------------------------------------------------------------- #
    # Preprocessing                                                            #
    # ---------------------------------------------------------------------- #

    def _preprocess(self, crop: np.ndarray) -> torch.Tensor:
        """Preprocess a BGR face crop for 6DRepNet.

        Matches the official SixDRepNet evaluation pipeline:
        1. BGR → RGB (single, explicit conversion).
        2. Resize shorter side then centre-crop to ``input_size`` × ``input_size``.
        3. Normalise pixel values to [0, 1].
        4. Apply ImageNet mean/std.
        5. Insert batch dimension and move to device.

        Args:
            crop: BGR uint8 numpy array ``(H, W, 3)``.

        Returns:
            Float32 tensor of shape ``(1, 3, H, W)`` on the inference device.
        """
        sz = self._config.input_size

        # 1. BGR → RGB (OpenCV images are BGR; the model was trained on RGB).
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

        # 2. Resize shorter side to sz, then centre-crop to sz × sz.
        h, w = rgb.shape[:2]
        if h < w:
            new_h, new_w = sz, int(w * sz / h)
        else:
            new_h, new_w = int(h * sz / w), sz
        resized = cv2.resize(rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Centre crop
        top  = (resized.shape[0] - sz) // 2
        left = (resized.shape[1] - sz) // 2
        cropped = resized[top : top + sz, left : left + sz]

        # 3. [0, 255] uint8 → [0, 1] float32
        norm = cropped.astype(np.float32) / 255.0

        # 4. ImageNet normalisation:  (pixel - mean) / std  channel-wise
        norm = (norm - _IMAGENET_MEAN) / _IMAGENET_STD

        # 5. HWC → CHW → BCHW, move to device
        tensor = (
            torch.from_numpy(norm)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .to(self._device)
        )
        return tensor
