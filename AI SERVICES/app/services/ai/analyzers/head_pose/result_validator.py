"""Result validation utilities."""

import numpy as np


class ResultValidator:
    """Validates head pose result values."""
    
    @staticmethod
    def is_valid_number(value: float) -> bool:
        """Check if value is a valid finite number.
        
        Args:
            value: Value to check.
            
        Returns:
            True if valid, False otherwise.
        """
        return value is not None and not np.isnan(value) and not np.isinf(value)
    
    @staticmethod
    def is_valid_bbox(bbox: tuple) -> bool:
        """Check if bounding box is valid.
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2).
            
        Returns:
            True if valid, False otherwise.
        """
        x1, y1, x2, y2 = bbox
        return x2 > x1 and y2 > y1 and x1 >= 0 and y1 >= 0
