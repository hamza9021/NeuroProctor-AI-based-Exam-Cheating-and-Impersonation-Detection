"""
Skeleton connections for pose visualization.

This module defines the skeleton connections between keypoints
for drawing pose skeletons on frames.
"""

from typing import List, Tuple


# COCO 17 keypoints skeleton connections
# Format: (keypoint_name_1, keypoint_name_2)
SKELETON_CONNECTIONS: List[Tuple[str, str]] = [
    ("nose", "left_eye"),
    ("nose", "right_eye"),
    ("left_eye", "left_ear"),
    ("right_eye", "right_ear"),
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("right_shoulder", "right_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("right_hip", "right_knee"),
    ("left_knee", "left_ankle"),
    ("right_knee", "right_ankle"),
]


def get_skeleton_connections() -> List[Tuple[str, str]]:
    """
    Get skeleton connections.

    Returns:
        List of keypoint connection tuples
    """
    return SKELETON_CONNECTIONS


def get_keypoint_pairs() -> List[Tuple[str, str]]:
    """
    Get keypoint pairs for skeleton drawing.

    Returns:
        List of keypoint name pairs
    """
    return SKELETON_CONNECTIONS
