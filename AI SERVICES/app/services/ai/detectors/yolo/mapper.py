"""YOLO class ID mapper."""

from app.services.ai.detectors.yolo.constants import TARGET_CLASSES


class ClassMapper:
    """Maps YOLO class IDs to human-readable names."""
    
    def __init__(self):
        """Initialize the mapper with target classes."""
        self._mapping = TARGET_CLASSES
    
    def get_class_name(self, class_id: int) -> str:
        """Get class name for a given class ID.
        
        Args:
            class_id: YOLO class ID.
            
        Returns:
            Class name or 'unknown' if not in mapping.
        """
        return self._mapping.get(class_id, "unknown")
    
    def is_target_class(self, class_id: int) -> bool:
        """Check if class ID is in target classes.
        
        Args:
            class_id: YOLO class ID.
            
        Returns:
            True if class is in target classes.
        """
        return class_id in self._mapping
