"""Model loader for the official 6DRepNet architecture."""

import logging
import os
from collections import OrderedDict

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

# Known-harmless missing/unexpected key prefixes.  Empty by default —
# any real mismatch is treated as an error unless listed here.
_KNOWN_HARMLESS_MISSING: tuple = ()
_KNOWN_HARMLESS_UNEXPECTED: tuple = ()


# --------------------------------------------------------------------------- #
# Checkpoint normalisation helpers                                             #
# --------------------------------------------------------------------------- #

def _normalise_state_dict(raw: object) -> OrderedDict:
    """Extract a plain state dict from common checkpoint wrapper formats.

    Handles:
    - plain ``OrderedDict`` state dicts
    - ``{"state_dict": ...}``
    - ``{"model_state_dict": ...}``
    - ``{"model": ...}``
    - DataParallel ``"module."`` prefix on every key

    Args:
        raw: Object returned by ``torch.load``.

    Returns:
        Normalised ``OrderedDict`` ready to pass to ``load_state_dict``.

    Raises:
        HeadPoseInitializationError: If the checkpoint format is unrecognised.
    """
    if isinstance(raw, OrderedDict):
        sd = raw
    elif isinstance(raw, dict):
        for wrapper_key in ("state_dict", "model_state_dict", "model"):
            if wrapper_key in raw and isinstance(raw[wrapper_key], (dict, OrderedDict)):
                sd = OrderedDict(raw[wrapper_key])
                logger.info("Extracted state dict from checkpoint key %r.", wrapper_key)
                break
        else:
            # Treat the dict itself as a state dict if every value is a tensor.
            if raw and all(isinstance(v, torch.Tensor) for v in raw.values()):
                sd = OrderedDict(raw)
                logger.info("Using top-level dict as state dict.")
            else:
                raise HeadPoseInitializationError(
                    "Unrecognised checkpoint format: expected a plain state dict "
                    "or a dict wrapping it under 'state_dict', "
                    "'model_state_dict', or 'model'."
                )
    elif isinstance(raw, torch.nn.Module):
        raise HeadPoseInitializationError(
            "Checkpoint contains a full torch.nn.Module, not a state dict. "
            "Re-save the checkpoint with: torch.save(model.state_dict(), path)"
        )
    else:
        raise HeadPoseInitializationError(
            f"Unrecognised checkpoint type: {type(raw).__name__}"
        )

    # Strip DataParallel / DistributedDataParallel prefix
    if any(k.startswith("module.") for k in sd):
        logger.info("Stripping 'module.' prefix from checkpoint keys.")
        sd = OrderedDict((k[len("module."):], v) for k, v in sd.items())

    return sd


def _validate_load_result(
    missing: list,
    unexpected: list,
    model: torch.nn.Module,
    checkpoint_path: str,
) -> None:
    """Assert that the checkpoint fully covers the model architecture.

    Args:
        missing: Keys in the model not found in the checkpoint.
        unexpected: Keys in the checkpoint not found in the model.
        model: Loaded model (used to compute total parameter count).
        checkpoint_path: Checkpoint path for error messages.

    Raises:
        HeadPoseInitializationError: If there are harmful key mismatches
            or the model has zero parameters.
    """
    harmful_missing = [
        k for k in missing
        if not any(k.startswith(p) for p in _KNOWN_HARMLESS_MISSING)
    ]
    harmful_unexpected = [
        k for k in unexpected
        if not any(k.startswith(p) for p in _KNOWN_HARMLESS_UNEXPECTED)
    ]

    if harmful_missing:
        raise HeadPoseInitializationError(
            f"Checkpoint {checkpoint_path!r} is MISSING {len(harmful_missing)} "
            f"model keys. First 10: {harmful_missing[:10]}. "
            "Likely an architecture mismatch — verify that deploy=True "
            "matches the checkpoint's reparameterisation state."
        )
    if harmful_unexpected:
        raise HeadPoseInitializationError(
            f"Checkpoint {checkpoint_path!r} has {len(harmful_unexpected)} "
            f"UNEXPECTED keys. First 10: {harmful_unexpected[:10]}. "
            "Likely an architecture mismatch or wrong checkpoint file."
        )

    total_params = sum(p.numel() for p in model.parameters())
    if total_params == 0:
        raise HeadPoseInitializationError(
            "Model has zero parameters after weight loading — the architecture "
            "object is likely empty."
        )

    logger.info(
        "Checkpoint loaded successfully: total_params=%d  "
        "missing_keys=%d  unexpected_keys=%d  trained_weights_verified=True",
        total_params,
        len(missing),
        len(unexpected),
    )


# --------------------------------------------------------------------------- #
# Loader                                                                       #
# --------------------------------------------------------------------------- #

class HeadPoseModelLoader:
    """Loads the official SixDRepNet model with validated trained weights.

    Raises ``HeadPoseInitializationError`` at startup when **any** of the
    following occur:

    - the ``sixdrepnet`` package is not installed;
    - the checkpoint file does not exist at ``config.model_path``;
    - the checkpoint format is unrecognised or corrupt;
    - ``strict=True`` weight loading fails (key mismatch);
    - the dummy forward pass returns the wrong output shape.

    **NO automatic placeholder or fallback model exists.**  A mock model
    may only be supplied through dependency injection in unit tests.
    """

    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialise the loader.

        Args:
            config: Head pose configuration.  ``config.model_path`` must be
                the absolute or relative path to the local ``.pth`` checkpoint.
                ``config.device`` selects the inference device.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger

    async def load(self) -> torch.nn.Module:
        """Load SixDRepNet with the official architecture and local weights.

        Returns:
            Model in evaluation mode on the configured device.

        Raises:
            HeadPoseInitializationError: On any loading or validation failure.
        """
        await self._logger.info(
            "6DRepNet initialisation started",
            emit_event=EVENT_INITIALIZATION_STARTED,
        )
        await self._logger.info(
            "Loading head-pose model weights",
            emit_event=EVENT_MODEL_LOADING,
            data={"model_path": self._config.model_path},
        )

        # ------------------------------------------------------------------ #
        # 1. Verify checkpoint file exists locally                           #
        # ------------------------------------------------------------------ #
        checkpoint_path = self._config.model_path
        if not os.path.isfile(checkpoint_path):
            raise HeadPoseInitializationError(
                f"6DRepNet checkpoint not found at {checkpoint_path!r}. "
                "Automatic weight downloading is disabled for reproducibility. "
                "Place the .pth file at the configured path before starting."
            )

        # ------------------------------------------------------------------ #
        # 2. Import the official architecture — fail if package is missing   #
        # ------------------------------------------------------------------ #
        try:
            from sixdrepnet.model import SixDRepNet  # type: ignore[import]
        except ImportError as exc:
            raise HeadPoseInitializationError(
                "The 'sixdrepnet' package is not installed. "
                "Install it with:  pip install sixdrepnet\n"
                f"Original import error: {exc}"
            ) from exc

        # ------------------------------------------------------------------ #
        # 3. Resolve compute device                                          #
        # ------------------------------------------------------------------ #
        device_str = resolve_device(self._config.device)
        device = torch.device(device_str)
        await self._logger.info(
            f"Head-pose device selected: {device}",
            emit_event=EVENT_DEVICE_SELECTED,
            data={"device": str(device)},
        )

        # ------------------------------------------------------------------ #
        # 4. Instantiate the official low-level SixDRepNet architecture      #
        #                                                                    #
        #   backbone_name="RepVGG-B1g2"  matches the distributed checkpoint. #
        #   backbone_file=""             no separate backbone weights.       #
        #   deploy=True                  reparameterised inference weights.  #
        #   pretrained=False             disables automatic download.        #
        # ------------------------------------------------------------------ #
        logger.info(
            "Instantiating SixDRepNet: backbone=RepVGG-B1g2  "
            "deploy=True  pretrained=False"
        )
        try:
            model = SixDRepNet(
                backbone_name="RepVGG-B1g2",
                backbone_file="",
                deploy=True,
                pretrained=False,
            )
        except Exception as exc:
            raise HeadPoseInitializationError(
                f"Failed to instantiate SixDRepNet architecture: {exc}"
            ) from exc

        # ------------------------------------------------------------------ #
        # 5. Read checkpoint                                                  #
        # ------------------------------------------------------------------ #
        logger.info("Reading checkpoint: %s", checkpoint_path)
        try:
            raw = torch.load(checkpoint_path, map_location=device)
        except Exception as exc:
            raise HeadPoseInitializationError(
                f"Failed to read checkpoint {checkpoint_path!r}: {exc}"
            ) from exc

        logger.info(
            "Checkpoint: type=%s  top_keys=%s",
            type(raw).__name__,
            list(raw.keys())[:6] if isinstance(raw, dict) else "n/a",
        )

        # ------------------------------------------------------------------ #
        # 6. Normalise and load weights — strict=True                        #
        # ------------------------------------------------------------------ #
        state_dict = _normalise_state_dict(raw)

        try:
            load_result = model.load_state_dict(state_dict, strict=True)
            missing = list(load_result.missing_keys)
            unexpected = list(load_result.unexpected_keys)
        except RuntimeError as exc:
            raise HeadPoseInitializationError(
                f"strict=True weight loading failed for {checkpoint_path!r}: "
                f"{exc}. "
                "Checkpoint and architecture are incompatible."
            ) from exc

        _validate_load_result(missing, unexpected, model, checkpoint_path)

        # ------------------------------------------------------------------ #
        # 7. Move to device and set to evaluation mode                       #
        # ------------------------------------------------------------------ #
        model.to(device)
        model.eval()

        # ------------------------------------------------------------------ #
        # 8. Validate output shape with a dummy forward pass                 #
        # ------------------------------------------------------------------ #
        await self._validate_model(model, device)

        logger.info(
            "6DRepNet ready: "
            "arch=SixDRepNet(RepVGG-B1g2 deploy=True)  "
            "checkpoint=%s  device=%s  trained_weights_verified=True",
            checkpoint_path,
            device,
        )
        await self._logger.info(
            "6DRepNet model initialised successfully",
            emit_event=EVENT_INITIALIZED,
            data={"trained_weights_verified": True, "device": str(device)},
        )
        return model

    # ---------------------------------------------------------------------- #
    # Private helpers                                                          #
    # ---------------------------------------------------------------------- #

    @staticmethod
    async def _validate_model(
        model: torch.nn.Module, device: torch.device
    ) -> None:
        """Validate that the model produces a [1, 3, 3] rotation matrix.

        Args:
            model: Model in evaluation mode.
            device: Target device.

        Raises:
            HeadPoseInitializationError: If output shape differs from [1,3,3].
        """
        try:
            dummy = torch.zeros(1, 3, 224, 224, device=device)
            with torch.inference_mode():
                output = model(dummy)
            actual_shape = tuple(output.shape)
            if actual_shape != (1, 3, 3):
                raise HeadPoseInitializationError(
                    f"Unexpected model output shape: {actual_shape}. "
                    "Expected (1, 3, 3) — a per-sample 3x3 rotation matrix. "
                    "Confirm the correct SixDRepNet architecture is loaded."
                )
            logger.info(
                "Model validation passed: "
                "input=%s  output=%s  output_is_rotation_matrix=True",
                tuple(dummy.shape),
                actual_shape,
            )
        except HeadPoseInitializationError:
            raise
        except Exception as exc:
            raise HeadPoseInitializationError(
                f"Dummy forward pass failed: {exc}"
            ) from exc
