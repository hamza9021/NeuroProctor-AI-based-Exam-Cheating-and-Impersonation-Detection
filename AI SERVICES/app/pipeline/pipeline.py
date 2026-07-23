"""
Pipeline module for AI Services.

This module provides the main Pipeline class that orchestrates
the video processing workflow with modular processors.
"""

from pathlib import Path
from typing import List, Optional
import numpy as np
from tqdm import tqdm

from ..video.reader import VideoReader
from ..video.writer import VideoWriter
from ..video.metadata import VideoMetadata
from ..processors.base_processor import BaseProcessor, PlaceholderProcessor
from ..config.settings import settings
from ..utils.logger import get_logger
from ..utils.timer import Timer


class Pipeline:
    """Main pipeline for video processing with modular processors."""

    def __init__(self, input_video: str, output_video: Optional[str] = None):
        """
        Initialize video processing pipeline.

        Args:
            input_video: Path to input video file
            output_video: Optional path for output video (auto-generated if not provided)
        """
        self.logger = get_logger(__name__)
        self.input_video = Path(input_video)
        self.output_video = self._generate_output_path(output_video)
        self.processors: List[BaseProcessor] = []
        self.timer = Timer()

        # Ensure directories exist
        settings.create_directories()

    def _generate_output_path(self, output_video: Optional[str]) -> Path:
        """
        Generate output path if not provided.

        Args:
            output_video: Optional output path

        Returns:
            Path object for output video
        """
        if output_video:
            return Path(output_video)
        
        # Auto-generate output filename
        output_name = f"processed_{self.input_video.stem}{self.input_video.suffix}"
        return settings.OUTPUT_DIR / output_name

    def add_processor(self, processor: BaseProcessor) -> None:
        """
        Add a processor to the pipeline.

        Args:
            processor: BaseProcessor instance to add
        """
        self.processors.append(processor)
        self.logger.info(f"Added processor: {processor.get_name()}")

    def remove_processor(self, processor_name: str) -> None:
        """
        Remove a processor from the pipeline by name.

        Args:
            processor_name: Name of processor to remove
        """
        self.processors = [p for p in self.processors if p.get_name() != processor_name]
        self.logger.info(f"Removed processor: {processor_name}")

    def clear_processors(self) -> None:
        """Clear all processors from the pipeline."""
        self.processors.clear()
        self.logger.info("Cleared all processors")

    def _initialize_processors(self) -> None:
        """Initialize all processors in the pipeline."""
        for processor in self.processors:
            try:
                processor.initialize()
                self.logger.info(f"Initialized processor: {processor.get_name()}")
            except Exception as e:
                self.logger.error(f"Failed to initialize processor {processor.get_name()}: {e}")
                raise

    def _cleanup_processors(self) -> None:
        """Cleanup all processors in the pipeline."""
        for processor in self.processors:
            try:
                processor.cleanup()
                self.logger.info(f"Cleaned up processor: {processor.get_name()}")
            except Exception as e:
                self.logger.error(f"Failed to cleanup processor {processor.get_name()}: {e}")

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame through all processors in sequence.

        Args:
            frame: Input frame

        Returns:
            Processed frame
        """
        processed_frame = frame.copy()
        
        for processor in self.processors:
            try:
                processed_frame = processor.process(processed_frame)
            except Exception as e:
                self.logger.error(f"Error in processor {processor.get_name()}: {e}")
                # Continue with original frame if processor fails
                continue
        
        return processed_frame

    def _display_progress(self, current: int, total: int) -> None:
        """
        Display processing progress.

        Args:
            current: Current frame number
            total: Total frames
        """
        percentage = (current / total) * 100
        bar_length = 20
        filled = int(bar_length * current / total)
        bar = '=' * filled + '-' * (bar_length - filled)
        
        self.logger.info(f"Progress: {bar} {percentage:.1f}% - Frame {current}/{total}")

    def run(self) -> VideoMetadata:
        """
        Execute the video processing pipeline.

        Returns:
            VideoMetadata of the processed video

        Raises:
            FileNotFoundError: If input video doesn't exist
            RuntimeError: If pipeline execution fails
        """
        self.timer.start()
        self.logger.info(f"Starting pipeline for: {self.input_video.name}")

        try:
            # Initialize video reader
            with VideoReader(str(self.input_video)) as reader:
                metadata = reader.get_metadata()
                self.logger.info(metadata.display())

                # Initialize video writer
                with VideoWriter(str(self.output_video), metadata) as writer:
                    # Initialize processors
                    if not self.processors:
                        # Add placeholder processor if none provided
                        self.logger.warning("No processors added, using placeholder processor")
                        self.add_processor(PlaceholderProcessor())
                    
                    self._initialize_processors()

                    # Process frames
                    total_frames = metadata.frame_count
                    self.logger.info(f"Processing started: {total_frames} frames")

                    # Use tqdm for progress bar
                    with tqdm(total=total_frames, desc="Processing", unit="frames") as pbar:
                        for frame_number, timestamp, frame in reader.read_frame():
                            # Update frame context for processors that need it
                            for processor in self.processors:
                                if hasattr(processor, 'set_frame_context'):
                                    processor.set_frame_context(frame_number, timestamp)
                            
                            # Process frame through pipeline
                            processed_frame = self._process_frame(frame)
                            
                            # Write processed frame
                            writer.write_frame(processed_frame)
                            
                            # Update progress
                            pbar.update(1)
                            pbar.set_postfix({
                                "frame": frame_number,
                                "time": f"{timestamp:.2f}s"
                            })

                            # Log progress periodically
                            if frame_number % 100 == 0:
                                self._display_progress(frame_number, total_frames)

                    self.logger.info("Processing completed")

                    # Cleanup processors
                    self._cleanup_processors()

            elapsed_time = self.timer.stop()
            self.logger.info(f"Pipeline completed in {self.timer.format_time(elapsed_time)}")
            self.logger.info(f"Output saved to: {self.output_video}")

            return metadata

        except FileNotFoundError as e:
            self.logger.error(f"Input video not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise RuntimeError(f"Pipeline execution failed: {e}")
