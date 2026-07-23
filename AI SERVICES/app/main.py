"""
Main entry point for AI Services module.

This script provides the command-line interface for running
the video processing pipeline.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline.pipeline import Pipeline
from app.config.settings import settings
from app.utils.logger import get_logger
from app.processors.object_detection_processor import ObjectDetectionProcessor


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="AI Services - Video Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input input_videos/exam.mp4
  python main.py --input input_videos/exam.mp4 --output output_videos/result.mp4
  python main.py --input input_videos/exam.mp4 --log-level DEBUG
        """
    )

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to input video file"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Path to output video file (auto-generated if not provided)"
    )

    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="AI Services Pipeline v2.0.0 (YOLO Object Detection)"
    )

    parser.add_argument(
        "--no-detection",
        action="store_true",
        help="Disable object detection (use placeholder processor)"
    )

    return parser.parse_args()


def validate_input_file(input_path: str) -> Path:
    """
    Validate input video file.

    Args:
        input_path: Path to input video

    Returns:
        Path object if valid

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file extension is not supported
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")
    
    if not settings.is_supported_extension(str(input_file)):
        raise ValueError(
            f"Unsupported file extension: {input_file.suffix}. "
            f"Supported extensions: {settings.SUPPORTED_EXTENSIONS}"
        )
    
    return input_file


def main():
    """Main execution function."""
    # Parse arguments
    args = parse_arguments()
    
    # Update settings with command-line arguments
    settings.LOG_LEVEL = args.log_level
    
    # Initialize logger
    logger = get_logger(__name__)
    
    try:
        # Validate input file
        input_file = validate_input_file(args.input)
        logger.info(f"Input file validated: {input_file}")
        
        # Create pipeline
        pipeline = Pipeline(
            input_video=str(input_file),
            output_video=args.output
        )
        
        # Add object detection processor (unless disabled)
        if not args.no_detection:
            logger.info("Adding Object Detection Processor to pipeline")
            detection_processor = ObjectDetectionProcessor()
            pipeline.add_processor(detection_processor)
        
        # Run pipeline
        logger.info("Starting video processing pipeline")
        metadata = pipeline.run()
        
        # Print summary
        logger.info("=" * 50)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        logger.info(f"Input:  {input_file}")
        logger.info(f"Output: {pipeline.output_video}")
        logger.info(f"Frames: {metadata.frame_count}")
        logger.info(f"Duration: {metadata.duration:.2f}s")
        logger.info("=" * 50)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
