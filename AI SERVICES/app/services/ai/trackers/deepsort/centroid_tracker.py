"""Simple centroid tracker for multi-object tracking."""

import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Tuple, Dict


class CentroidTracker:
    """Simple centroid-based tracker for multi-object tracking.
    
    Uses Euclidean distance between centroids to match detections
    to existing tracks. Alternative to DeepSORT when dependencies fail.
    """
    
    def __init__(self, max_disappeared: int = 30, min_hits: int = 3):
        """Initialize centroid tracker.
        
        Args:
            max_disappeared: Maximum frames a track can be missing.
            min_hits: Minimum detections before track is confirmed.
        """
        self._next_id = 0
        self._objects: Dict[int, np.ndarray] = {}
        self._bboxes: Dict[int, list] = {}
        self._disappeared: Dict[int, int] = {}
        self._hits: Dict[int, int] = {}
        self._max_disappeared = max_disappeared
        self._min_hits = min_hits
    
    def register(self, centroid: np.ndarray, bbox: list) -> int:
        """Register a new track.
        
        Args:
            centroid: Centroid coordinates [x, y].
            bbox: Original detection bounding box [x1, y1, x2, y2].
            
        Returns:
            Track ID.
        """
        self._objects[self._next_id] = centroid
        self._bboxes[self._next_id] = bbox
        self._disappeared[self._next_id] = 0
        self._hits[self._next_id] = 1
        track_id = self._next_id
        self._next_id += 1
        return track_id
    
    def deregister(self, track_id: int):
        """Deregister a track.
        
        Args:
            track_id: Track ID to deregister.
        """
        del self._objects[track_id]
        del self._bboxes[track_id]
        del self._disappeared[track_id]
        del self._hits[track_id]
    
    def update(self, detections: List[np.ndarray]) -> List[Dict]:
        """Update tracker with new detections.
        
        Args:
            detections: List of bounding boxes as [x1, y1, x2, y2].
            
        Returns:
            List of track dictionaries with track_id, bbox, etc.
        """
        if len(detections) == 0:
            # Mark all tracks as disappeared
            for track_id in list(self._disappeared.keys()):
                self._disappeared[track_id] += 1
                if self._disappeared[track_id] > self._max_disappeared:
                    self.deregister(track_id)
            return []
        
        # Calculate centroids for detections
        input_centroids = np.zeros((len(detections), 2), dtype="int")
        for i, (x1, y1, x2, y2) in enumerate(detections):
            input_centroids[i] = [(x1 + x2) // 2, (y1 + y2) // 2]
        
        # If no existing tracks, register all
        if len(self._objects) == 0:
            for i, centroid in enumerate(input_centroids):
                self.register(centroid, list(detections[i]))
        else:
            # Match detections to existing tracks
            object_centroids = list(self._objects.values())
            object_ids = list(self._objects.keys())
            
            # Calculate distances
            D = cdist(object_centroids, input_centroids)
            
            # Find minimum distance for each track
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_row_indices = set()
            used_col_indices = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_row_indices or col in used_col_indices:
                    continue
                
                # Update track centroid and bbox
                track_id = object_ids[row]
                self._objects[track_id] = input_centroids[col]
                self._bboxes[track_id] = list(detections[col])
                self._disappeared[track_id] = 0
                self._hits[track_id] += 1
                
                used_row_indices.add(row)
                used_col_indices.add(col)
            
            # Register unmatched detections
            unused_col_indices = set(range(0, D.shape[1])).difference(used_col_indices)
            if D.shape[0] < D.shape[1]:
                for col in unused_col_indices:
                    self.register(input_centroids[col], list(detections[col]))
        
        # Build track list
        tracks = []
        for track_id, centroid in self._objects.items():
            tracks.append({
                'track_id': track_id,
                'bbox': self._bboxes[track_id],
                'centroid': centroid,
                'is_confirmed': self._hits[track_id] >= self._min_hits,
                'age': self._hits[track_id],
                'hits': self._hits[track_id],
                'time_since_update': self._disappeared[track_id],
            })
        
        return tracks
