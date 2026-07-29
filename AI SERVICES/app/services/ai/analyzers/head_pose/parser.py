"""Parser for 6DRepNet rotation-matrix output.

The official SixDRepNet forward method returns a rotation matrix with shape
``(3, 3)`` per sample (batch dimension already squeezed by the estimator).

This parser:

1. Validates the shape is exactly ``(3, 3)``.
2. Converts the rotation matrix to Euler angles using the same formula as the
   official 6DRepNet ``compute_euler_angles_from_rotation_matrices`` utility.
3. Maps the angle indices explicitly:

       index 0 → pitch  (x-axis rotation, nose up/down)
       index 1 → yaw    (y-axis rotation, head left/right)
       index 2 → roll   (z-axis rotation, tilt)

4. Converts from radians to degrees **exactly once**.
5. Returns ``(yaw_deg, pitch_deg, roll_deg)`` to match the contract expected
   by ``TrackProcessor``.
"""

import logging
from typing import Tuple

import numpy as np

from app.services.ai.analyzers.head_pose.constants import (
    AXIS_PITCH,
    AXIS_ROLL,
    AXIS_YAW,
    EVENT_RESULT_PARSED,
)
from app.services.ai.analyzers.head_pose.exceptions import HeadPoseParsingError
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


def _rotation_matrix_to_euler(R: np.ndarray) -> Tuple[float, float, float]:
    """Convert a 3×3 rotation matrix to Euler angles in radians.

    Implements the same algorithm used by the official 6DRepNet repository
    (``compute_euler_angles_from_rotation_matrices``).

    Convention:
        - pitch  (x-rotation) = ``atan2( R[2,1],  R[2,2])``
        - yaw    (y-rotation) = ``atan2(-R[2,0],  sy     )``
        - roll   (z-rotation) = ``atan2( R[1,0],  R[0,0])``

    where ``sy = sqrt(R[0,0]^2 + R[1,0]^2)``.  When ``sy`` is near zero
    (gimbal-lock singularity), the singular branch is used:
        - pitch = ``atan2(-R[1,2],  R[1,1])``
        - yaw   = ``atan2(-R[2,0],  sy    )``
        - roll  = 0

    Args:
        R: 3×3 float32/float64 rotation matrix, shape ``(3, 3)``.

    Returns:
        ``(pitch_rad, yaw_rad, roll_rad)`` all in radians.
    """
    sy = float(np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2))
    singular = sy < 1e-6

    if not singular:
        pitch_rad = float(np.arctan2( R[2, 1],  R[2, 2]))
        yaw_rad   = float(np.arctan2(-R[2, 0],  sy))
        roll_rad  = float(np.arctan2( R[1, 0],  R[0, 0]))
    else:
        # Gimbal-lock fallback
        pitch_rad = float(np.arctan2(-R[1, 2],  R[1, 1]))
        yaw_rad   = float(np.arctan2(-R[2, 0],  sy))
        roll_rad  = 0.0

    return pitch_rad, yaw_rad, roll_rad


class HeadPoseParser:
    """Parses a 3×3 SixDRepNet rotation matrix into yaw, pitch and roll.

    Input contract (from ``HeadPoseEstimator.estimate``):
        ``numpy.ndarray`` of shape ``(3, 3)`` — the rotation matrix for one
        face crop.

    Output contract (to ``TrackProcessor``):
        ``(yaw_deg, pitch_deg, roll_deg)`` — three ``float`` values in degrees.
    """

    def __init__(self, pipeline_logger: PipelineLogger):
        """Initialise the parser.

        Args:
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._logger = pipeline_logger

    async def parse(
        self, rotation_matrix: np.ndarray, track_id: int
    ) -> Tuple[float, float, float]:
        """Convert rotation matrix to yaw, pitch, roll in degrees.

        Args:
            rotation_matrix: numpy array of shape ``(3, 3)`` produced by
                ``HeadPoseEstimator.estimate``.  Must be a valid rotation
                matrix (orthogonal, det ≈ +1).
            track_id: DeepSORT track ID — used only for logging.

        Returns:
            ``(yaw_deg, pitch_deg, roll_deg)`` as Python floats.

        Raises:
            HeadPoseParsingError: If the input shape is not ``(3, 3)`` or
                conversion fails.
        """
        try:
            # ---------------------------------------------------------------- #
            # 1. Validate input shape                                           #
            # ---------------------------------------------------------------- #
            if (
                not isinstance(rotation_matrix, np.ndarray)
                or rotation_matrix.shape != (3, 3)
            ):
                got = (
                    rotation_matrix.shape
                    if isinstance(rotation_matrix, np.ndarray)
                    else type(rotation_matrix).__name__
                )
                raise HeadPoseParsingError(
                    f"Expected rotation matrix of shape (3, 3) for "
                    f"Track #{track_id}, got {got}."
                )

            # Log rotation matrix for diagnostic purposes
            logger.debug(
                "Rotation matrix  track_id=%d  det=%.4f\n%s",
                track_id,
                float(np.linalg.det(rotation_matrix)),
                rotation_matrix,
            )

            # ---------------------------------------------------------------- #
            # 2. Convert rotation matrix → Euler angles (radians)              #
            # ---------------------------------------------------------------- #
            pitch_rad, yaw_rad, roll_rad = _rotation_matrix_to_euler(rotation_matrix)

            # ---------------------------------------------------------------- #
            # 3. Radians → degrees  (exactly once, here)                       #
            # ---------------------------------------------------------------- #
            pitch_deg = float(np.degrees(pitch_rad))
            yaw_deg   = float(np.degrees(yaw_rad))
            roll_deg  = float(np.degrees(roll_rad))

            # ---------------------------------------------------------------- #
            # 4. Emit parsed event                                              #
            # ---------------------------------------------------------------- #
            logger.debug(
                "Parsed angles  track_id=%d  "
                "pitch=%.2f deg  yaw=%.2f deg  roll=%.2f deg",
                track_id, pitch_deg, yaw_deg, roll_deg,
            )

            await self._logger.info(
                f"Yaw: {yaw_deg:.1f}°, Pitch: {pitch_deg:.1f}°, Roll: {roll_deg:.1f}°",
                emit_event=EVENT_RESULT_PARSED,
                data={
                    "track_id": track_id,
                    AXIS_YAW:   yaw_deg,
                    AXIS_PITCH: pitch_deg,
                    AXIS_ROLL:  roll_deg,
                },
            )

            return yaw_deg, pitch_deg, roll_deg

        except HeadPoseParsingError:
            raise
        except Exception as exc:
            logger.error(
                "Parsing failed for Track #%d: %s", track_id, exc, exc_info=True
            )
            raise HeadPoseParsingError(f"Parsing failed: {exc}") from exc
