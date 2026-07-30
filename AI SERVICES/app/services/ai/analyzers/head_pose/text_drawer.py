"""Text drawer for head pose annotations."""

import logging
from typing import List, Tuple

import cv2
import numpy as np

from app.services.ai.analyzers.head_pose.constants import (
    LABEL_PITCH,
    LABEL_ROLL,
    LABEL_YAW,
)
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult

logger = logging.getLogger(__name__)

# Visual constants
_FONT = cv2.FONT_HERSHEY_SIMPLEX
_FONT_SCALE = 0.50
_FONT_THICKNESS = 1
_LINE_HEIGHT = 18          # pixels between baselines
_PAD_X = 5                 # horizontal padding inside the background rect
_PAD_Y = 3                 # vertical padding inside the background rect
_BG_ALPHA = 0.55           # background rectangle opacity


class TextDrawer:
    """Draws text labels for head pose results.

    Labels are rendered downward in the order:
        ID → Roll → Yaw → Pitch

    The block is positioned relative to the person bounding box with
    automatic frame-boundary clamping and a semi-transparent background.
    """

    def draw(self, frame: np.ndarray, result: HeadPoseResult) -> None:
        """Draw head pose text on frame.

        Args:
            frame: BGR frame to draw on (modified in-place).
            result: Head pose result containing angles and bounding boxes.
        """
        frame_h, frame_w = frame.shape[:2]

        # ------------------------------------------------------------------ #
        # Build label list in the required order: ID → Roll → Yaw → Pitch    #
        # ------------------------------------------------------------------ #
        labels: List[str] = [
            f"ID: {result.track_id}",
            f"{LABEL_ROLL}: {result.roll:.1f}\u00b0",
            f"{LABEL_YAW}: {result.yaw:.1f}\u00b0",
            f"{LABEL_PITCH}: {result.pitch:.1f}\u00b0",
        ]

        # ------------------------------------------------------------------ #
        # Compute the bounding box used for positioning                        #
        # Prefer the full person bbox; fall back to the face bbox.            #
        # ------------------------------------------------------------------ #
        ref_bbox = result.person_bbox if result.person_bbox is not None else result.face_bbox
        rx1, ry1, rx2, ry2 = [int(v) for v in ref_bbox]

        # ------------------------------------------------------------------ #
        # Measure text block                                                   #
        # ------------------------------------------------------------------ #
        total_height = _LINE_HEIGHT * len(labels) + _PAD_Y * 2
        max_text_w = max(
            cv2.getTextSize(lbl, _FONT, _FONT_SCALE, _FONT_THICKNESS)[0][0]
            for lbl in labels
        )
        block_w = max_text_w + _PAD_X * 2

        # ------------------------------------------------------------------ #
        # Choose Y: prefer below person bbox to avoid Person label overlap   #
        # Place above only if near bottom edge                                #
        # ------------------------------------------------------------------ #
        preferred_bottom_y = ry2 + 4
        if preferred_bottom_y + total_height > frame_h - 5:
            # Place above the person-bbox bottom instead
            text_top_y = max(ry1 - total_height - 4, 5)
        else:
            text_top_y = preferred_bottom_y

        # Clamp to frame
        text_top_y = max(5, min(text_top_y, frame_h - total_height - 5))

        # ------------------------------------------------------------------ #
        # Choose X: align to ref-bbox left; clamp to frame                    #
        # ------------------------------------------------------------------ #
        text_x = max(5, min(rx1, frame_w - block_w - 5))

        # ------------------------------------------------------------------ #
        # Draw semi-transparent background rectangle                           #
        # ------------------------------------------------------------------ #
        bg_x1 = text_x - _PAD_X
        bg_y1 = text_top_y - _PAD_Y
        bg_x2 = bg_x1 + block_w
        bg_y2 = bg_y1 + total_height

        # Clamp rectangle to frame
        bg_x1 = max(0, bg_x1)
        bg_y1 = max(0, bg_y1)
        bg_x2 = min(frame_w - 1, bg_x2)
        bg_y2 = min(frame_h - 1, bg_y2)

        overlay = frame.copy()
        cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        cv2.addWeighted(overlay, _BG_ALPHA, frame, 1.0 - _BG_ALPHA, 0, frame)

        # ------------------------------------------------------------------ #
        # Draw each label line from top downward                               #
        # ------------------------------------------------------------------ #
        y_cursor = text_top_y + _PAD_Y + _LINE_HEIGHT - 4  # first baseline
        for line in labels:
            # Clamp baseline to frame before drawing
            if 0 < y_cursor < frame_h:
                cv2.putText(
                    frame,
                    line,
                    (text_x, y_cursor),
                    _FONT,
                    _FONT_SCALE,
                    (0, 255, 0),
                    _FONT_THICKNESS,
                    cv2.LINE_AA,
                )
            y_cursor += _LINE_HEIGHT

        # ------------------------------------------------------------------ #
        # Debug log                                                            #
        # ------------------------------------------------------------------ #
        logger.debug(
            "track_id=%d  roll=%.1f  yaw=%.1f  pitch=%.1f  "
            "text_position=(%d, %d)  axis_origin=%s  face_bbox=%s",
            result.track_id,
            result.roll,
            result.yaw,
            result.pitch,
            text_x,
            text_top_y,
            result.axis_origin,
            result.face_bbox,
        )

