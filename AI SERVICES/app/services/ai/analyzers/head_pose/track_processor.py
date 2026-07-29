"""Track processor for single track head pose estimation."""

from app.services.ai.analyzers.head_pose.cropper import FaceCropper
from app.services.ai.analyzers.head_pose.estimator import HeadPoseEstimator
from app.services.ai.analyzers.head_pose.face_locator import FaceLocator
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult
from app.services.ai.analyzers.head_pose.parser import HeadPoseParser
from app.services.ai.analyzers.head_pose.validator import HeadPoseValidator
from app.services.ai.pipeline.context import FrameContext


class TrackProcessor:
    """Processes a single track for head pose estimation."""
    
    def __init__(
        self,
        locator: FaceLocator,
        cropper: FaceCropper,
        estimator: HeadPoseEstimator,
        parser: HeadPoseParser,
        validator: HeadPoseValidator,
    ):
        """Initialize track processor.
        
        Args:
            locator: Face locator.
            cropper: Face cropper.
            estimator: Head pose estimator.
            parser: Output parser.
            validator: Result validator.
        """
        self._locator = locator
        self._cropper = cropper
        self._estimator = estimator
        self._parser = parser
        self._validator = validator
    
    async def process(self, context: FrameContext, track) -> HeadPoseResult:
        """Process a single track.
        
        Args:
            context: FrameContext.
            track: Track to process.
            
        Returns:
            HeadPoseResult.
        """
        # Get pose data for this track
        pose_data = None
        if hasattr(context, "poses"):
            for pose in context.poses:
                if hasattr(pose, "track_id") and pose.track_id == track.track_id:
                    pose_data = {"keypoints": pose.keypoints}
                    break
        
        # Locate face region
        face_bbox = await self._locator.locate(
            track.track_id, track.bbox, pose_data, context.frame.shape[:2]
        )
        
        # Crop face
        crop = await self._cropper.crop(context.frame, face_bbox, track.track_id)
        
        # Estimate head pose
        raw_output = await self._estimator.estimate(crop, track.track_id)
        
        # Parse output
        yaw, pitch, roll = await self._parser.parse(raw_output, track.track_id)
        
        # Validate result
        is_valid = await self._validator.validate(
            track.track_id, face_bbox, yaw, pitch, roll
        )
        
        return HeadPoseResult(
            track_id=track.track_id,
            face_bbox=face_bbox,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            is_valid=is_valid,
        )
