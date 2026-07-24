"""
Head pose estimation utility functions.

This module provides helper functions for head pose estimation,
including visualization, angle calculations, and data processing.
"""

import numpy as np
import cv2
from typing import Tuple, List, Optional
import math

from app.head_pose.schemas import HeadPoseResult


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to [-90, 90] range.
    
    Args:
        angle: Angle in degrees
        
    Returns:
        Normalized angle in [-90, 90]
    """
    while angle > 90:
        angle -= 180
    while angle < -90:
        angle += 180
    return angle


def angle_to_radians(angle: float) -> float:
    """
    Convert angle from degrees to radians.
    
    Args:
        angle: Angle in degrees
        
    Returns:
        Angle in radians
    """
    return angle * math.pi / 180.0


def radians_to_angle(radians: float) -> float:
    """
    Convert angle from radians to degrees.
    
    Args:
        radians: Angle in radians
        
    Returns:
        Angle in degrees
    """
    return radians * 180.0 / math.pi


def calculate_euler_distance(
    yaw1: float,
    pitch1: float,
    roll1: float,
    yaw2: float,
    pitch2: float,
    roll2: float,
) -> float:
    """
    Calculate Euclidean distance between two head orientations.
    
    Args:
        yaw1, pitch1, roll1: First orientation in degrees
        yaw2, pitch2, roll2: Second orientation in degrees
        
    Returns:
        Euclidean distance
    """
    return math.sqrt(
        (yaw1 - yaw2) ** 2 +
        (pitch1 - pitch2) ** 2 +
        (roll1 - roll2) ** 2
    )


def is_significant_head_movement(
    yaw1: float,
    pitch1: float,
    roll1: float,
    yaw2: float,
    pitch2: float,
    roll2: float,
    threshold: float = 15.0,
) -> bool:
    """
    Check if there is significant head movement between two orientations.
    
    Args:
        yaw1, pitch1, roll1: First orientation in degrees
        yaw2, pitch2, roll2: Second orientation in degrees
        threshold: Movement threshold in degrees
        
    Returns:
        True if significant movement, False otherwise
    """
    distance = calculate_euler_distance(yaw1, pitch1, roll1, yaw2, pitch2, roll2)
    return distance > threshold


def draw_head_pose(
    frame: np.ndarray,
    head_pose: HeadPoseResult,
    bbox: Tuple[int, int, int, int],
    color: Tuple[int, int, int] = (0, 255, 255),
    font_scale: float = 0.5,
) -> np.ndarray:
    """
    Draw head pose visualization on frame.
    
    Args:
        frame: Input frame (H, W, 3)
        head_pose: HeadPoseResult to visualize
        bbox: Bounding box for positioning text
        color: Text color (B, G, R)
        font_scale: Font scale for text
        
    Returns:
        Frame with head pose visualization
    """
    x1, y1, x2, y2 = bbox
    
    # Calculate face center
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    # Draw 3D axis visualization (yaw, pitch, roll)
    axis_length = min(x2 - x1, y2 - y1) // 3
    
    # Calculate axis endpoints based on head orientation
    # X-axis (red) - represents yaw
    yaw_rad = angle_to_radians(head_pose.yaw)
    x_end_x = center_x + int(axis_length * math.cos(yaw_rad))
    x_end_y = center_y + int(axis_length * math.sin(yaw_rad))
    
    # Y-axis (green) - represents pitch
    pitch_rad = angle_to_radians(head_pose.pitch)
    y_end_x = center_x + int(axis_length * math.cos(pitch_rad + math.pi/2))
    y_end_y = center_y - int(axis_length * math.sin(pitch_rad))
    
    # Z-axis (blue) - represents roll
    roll_rad = angle_to_radians(head_pose.roll)
    z_end_x = center_x + int(axis_length * math.cos(roll_rad))
    z_end_y = center_y + int(axis_length * math.sin(roll_rad))
    
    # Draw axes with thickness
    cv2.line(frame, (center_x, center_y), (x_end_x, x_end_y), (0, 0, 255), 4)  # Red - X
    cv2.line(frame, (center_x, center_y), (y_end_x, y_end_y), (0, 255, 0), 4)  # Green - Y
    cv2.line(frame, (center_x, center_y), (z_end_x, z_end_y), (255, 0, 0), 4)  # Blue - Z
    
    # Draw center point
    cv2.circle(frame, (center_x, center_y), 5, (255, 255, 255), -1)
    
    # Draw face crop bounding box if available
    if head_pose.face_crop_bbox:
        fx1, fy1, fx2, fy2 = head_pose.face_crop_bbox
        cv2.rectangle(frame, (fx1, fy1), (fx2, fy2), (0, 255, 255), 2)
    
    # Position text above bounding box
    text_x = x1
    text_y = max(30, y1 - 10)
    
    # Draw background for text
    text_lines = [
        f"ID: {head_pose.track_id}",
        f"Yaw: {head_pose.yaw:.1f}°",
        f"Pitch: {head_pose.pitch:.1f}°",
        f"Roll: {head_pose.roll:.1f}°"
    ]
    
    for i, line in enumerate(text_lines):
        (text_width, text_height), _ = cv2.getTextSize(
            line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2
        )
        cv2.rectangle(
            frame,
            (text_x - 2, text_y - text_height - 2 - i * 25),
            (text_x + text_width + 2, text_y + 2 - i * 25),
            (0, 0, 0),
            -1
        )
    
    # Draw track ID
    cv2.putText(
        frame,
        f"ID: {head_pose.track_id}",
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        2,
    )
    
    # Draw yaw
    cv2.putText(
        frame,
        f"Yaw: {head_pose.yaw:.1f}°",
        (text_x, text_y - 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        2,
    )
    
    # Draw pitch
    cv2.putText(
        frame,
        f"Pitch: {head_pose.pitch:.1f}°",
        (text_x, text_y - 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        2,
    )
    
    # Draw roll
    cv2.putText(
        frame,
        f"Roll: {head_pose.roll:.1f}°",
        (text_x, text_y - 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        2,
    )
    
    return frame


def draw_head_pose_arrow(
    frame: np.ndarray,
    center: Tuple[int, int],
    yaw: float,
    pitch: float,
    length: int = 50,
    color: Tuple[int, int, int] = (0, 255, 255),
    thickness: int = 3,
) -> np.ndarray:
    """
    Draw 3D orientation arrow for head pose.
    
    Args:
        frame: Input frame (H, W, 3)
        center: Center point (x, y)
        yaw: Yaw angle in degrees
        pitch: Pitch angle in degrees
        length: Arrow length
        color: Arrow color (B, G, R)
        thickness: Line thickness
        
    Returns:
        Frame with orientation arrow
    """
    cx, cy = center
    
    # Calculate arrow end based on yaw and pitch
    end_x = cx + int(length * math.sin(angle_to_radians(yaw)))
    end_y = cy - int(length * math.sin(angle_to_radians(pitch)))
    
    # Draw main line
    cv2.line(frame, (cx, cy), (end_x, end_y), color, thickness)
    
    # Draw arrow head
    arrow_size = 10
    angle = math.atan2(end_y - cy, end_x - cx)
    
    # Arrow head points
    p1 = (
        int(end_x - arrow_size * math.cos(angle - math.pi / 6)),
        int(end_y - arrow_size * math.sin(angle - math.pi / 6))
    )
    p2 = (
        int(end_x - arrow_size * math.cos(angle + math.pi / 6)),
        int(end_y - arrow_size * math.sin(angle + math.pi / 6))
    )
    
    cv2.line(frame, (end_x, end_y), p1, color, thickness)
    cv2.line(frame, (end_x, end_y), p2, color, thickness)
    
    return frame


def smooth_head_pose(
    poses: List[HeadPoseResult],
    window_size: int = 5,
) -> List[HeadPoseResult]:
    """
    Apply temporal smoothing to head pose estimates.
    
    Args:
        poses: List of HeadPoseResult to smooth
        window_size: Size of smoothing window
        
    Returns:
        List of smoothed HeadPoseResult
    """
    if len(poses) < window_size:
        return poses
    
    smoothed_poses = []
    
    for i in range(len(poses)):
        # Get window
        start = max(0, i - window_size // 2)
        end = min(len(poses), i + window_size // 2 + 1)
        window = poses[start:end]
        
        # Calculate average angles
        avg_yaw = sum(p.yaw for p in window) / len(window)
        avg_pitch = sum(p.pitch for p in window) / len(window)
        avg_roll = sum(p.roll for p in window) / len(window)
        avg_confidence = sum(p.confidence for p in window) / len(window)
        
        # Create smoothed pose
        smoothed_pose = HeadPoseResult(
            track_id=poses[i].track_id,
            frame_number=poses[i].frame_number,
            timestamp=poses[i].timestamp,
            yaw=avg_yaw,
            pitch=avg_pitch,
            roll=avg_roll,
            confidence=avg_confidence,
            face_crop_bbox=poses[i].face_crop_bbox,
            metadata=poses[i].metadata,
        )
        
        smoothed_poses.append(smoothed_pose)
    
    return smoothed_poses


def calculate_head_pose_statistics(
    poses: List[HeadPoseResult],
) -> dict:
    """
    Calculate statistics for head pose estimates.
    
    Args:
        poses: List of HeadPoseResult
        
    Returns:
        Dictionary with statistics
    """
    if not poses:
        return {}
    
    yaws = [p.yaw for p in poses]
    pitches = [p.pitch for p in poses]
    rolls = [p.roll for p in poses]
    confidences = [p.confidence for p in poses]
    
    return {
        'count': len(poses),
        'yaw_mean': np.mean(yaws),
        'yaw_std': np.std(yaws),
        'yaw_min': np.min(yaws),
        'yaw_max': np.max(yaws),
        'pitch_mean': np.mean(pitches),
        'pitch_std': np.std(pitches),
        'pitch_min': np.min(pitches),
        'pitch_max': np.max(pitches),
        'roll_mean': np.mean(rolls),
        'roll_std': np.std(rolls),
        'roll_min': np.min(rolls),
        'roll_max': np.max(rolls),
        'confidence_mean': np.mean(confidences),
        'confidence_min': np.min(confidences),
    }


# Add sixdrepnet utils functions to avoid import conflicts
import torch

def normalize_vector(v):
    batch = v.shape[0]
    v_mag = torch.sqrt(v.pow(2).sum(1))
    gpu = v_mag.get_device()
    if gpu < 0:
        eps = torch.autograd.Variable(torch.FloatTensor([1e-8])).to(torch.device('cpu'))
    else:
        eps = torch.autograd.Variable(torch.FloatTensor([1e-8])).to(torch.device('cuda:%d' % gpu))
    v_mag = torch.max(v_mag, eps)
    v_mag = v_mag.view(batch,1).expand(batch,v.shape[1])
    v = v/v_mag
    return v
    
def cross_product(u, v):
    batch = u.shape[0]
    i = u[:,1]*v[:,2] - u[:,2]*v[:,1]
    j = u[:,2]*v[:,0] - u[:,0]*v[:,2]
    k = u[:,0]*v[:,1] - u[:,1]*v[:,0]
    out = torch.cat((i.view(batch,1), j.view(batch,1), k.view(batch,1)),1)
    return out
    
def compute_rotation_matrix_from_ortho6d(poses):
    x_raw = poses[:,0:3]
    y_raw = poses[:,3:6]
    x = normalize_vector(x_raw)
    z = cross_product(x,y_raw)
    z = normalize_vector(z)
    y = cross_product(z,x)
    x = x.view(-1,3,1)
    y = y.view(-1,3,1)
    z = z.view(-1,3,1)
    matrix = torch.cat((x,y,z), 2)
    return matrix

def compute_euler_angles_from_rotation_matrices(rotation_matrices):
    batch = rotation_matrices.shape[0]
    R = rotation_matrices
    sy = torch.sqrt(R[:,0,0]*R[:,0,0]+R[:,1,0]*R[:,1,0])
    singular = sy<1e-6
    singular = singular.float()
    x = torch.atan2(R[:,2,1], R[:,2,2])
    y = torch.atan2(-R[:,2,0], sy)
    z = torch.atan2(R[:,1,0],R[:,0,0])
    xs = torch.atan2(-R[:,1,2], R[:,1,1])
    ys = torch.atan2(-R[:,2,0], sy)
    zs = R[:,1,0]*0
    gpu = rotation_matrices.get_device()
    if gpu < 0:
        out_euler = torch.autograd.Variable(torch.zeros(batch,3)).to(torch.device('cpu'))
    else:
        out_euler = torch.autograd.Variable(torch.zeros(batch,3)).to(torch.device('cuda:%d' % gpu))
    out_euler[:,0] = x*(1-singular)+xs*singular
    out_euler[:,1] = y*(1-singular)+ys*singular
    out_euler[:,2] = z*(1-singular)+zs*singular
    return out_euler
