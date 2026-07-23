# AI Services - Video Processing Pipeline

Phase 1: Offline Video Processing Infrastructure for NeuroProctor

## Overview

This module provides a clean, modular offline video processing pipeline designed for the NeuroProctor AI examination system. It serves as the foundation for future AI model integration while maintaining complete independence from the FastAPI backend.

## Features

- **Modular Architecture**: Clean separation of concerns with reusable components
- **Video Processing**: Frame-by-frame video reading and writing
- **Metadata Extraction**: Automatic extraction of video properties
- **Progress Tracking**: Real-time progress bars and logging
- **Error Handling**: Comprehensive error handling for corrupted files
- **Extensible Design**: Easy integration of future AI processors
- **Structured Logging**: Dual console and file logging
- **Configuration Management**: Centralized settings management

## Project Structure

```
AI Services/
├── app/
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── pipeline.py          # Main pipeline orchestration
│   ├── video/
│   │   ├── __init__.py
│   │   ├── reader.py            # Video reader implementation
│   │   ├── writer.py            # Video writer implementation
│   │   └── metadata.py          # Video metadata class
│   ├── processors/
│   │   ├── __init__.py
│   │   └── base_processor.py    # Abstract base processor
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # Logging utilities
│   │   └── timer.py             # Timing utilities
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration settings
│   ├── __init__.py
│   └── main.py                  # CLI entry point
├── input_videos/               # Input video directory
├── output_videos/              # Output video directory
├── logs/                       # Log files directory
├── temp/                       # Temporary files directory
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Installation

1. Navigate to the AI Services directory:
```bash
cd "AI Services"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Process a video with default settings:
```bash
python app/main.py --input input_videos/exam.mp4
```

### Specify Output Path

Process a video with custom output path:
```bash
python app/main.py --input input_videos/exam.mp4 --output output_videos/result.mp4
```

### Set Log Level

Process with debug logging:
```bash
python app/main.py --input input_videos/exam.mp4 --log-level DEBUG
```

### Command-Line Options

```
--input, -i      Path to input video file (required)
--output, -o     Path to output video file (optional, auto-generated)
--log-level, -l  Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
--version, -v    Show version information
--help, -h       Show help message
```

## Architecture

### Video Reader

The `VideoReader` class handles:
- File validation and opening
- Metadata extraction (FPS, resolution, frame count, duration, codec)
- Sequential frame reading with timestamps
- Graceful handling of corrupted frames

### Video Writer

The `VideoWriter` class handles:
- Automatic output directory creation
- Codec preservation
- Resolution and FPS preservation
- Frame writing with validation

### Pipeline

The `Pipeline` class orchestrates:
- Video loading and metadata extraction
- Sequential frame processing through processors
- Progress tracking and logging
- Output video generation

### Base Processor

The `BaseProcessor` abstract class defines:
- Standard interface for all processors
- Configuration management
- Context manager support
- Placeholder processor for testing

## Future AI Pipeline

The architecture supports this exact pipeline in future phases:

```
Video Reader
      │
      ▼
YOLO Object Detection
      │
      ▼
Face Recognition
      │
      ▼
YOLO Pose
      │
      ▼
VideoMAE
      │
      ▼
Feature Fusion
      │
      ▼
Temporal Smoothing
      │
      ▼
Rule Engine
      │
      ▼
Report Generator
```

## Example: Adding a Custom Processor

```python
from app.processors.base_processor import BaseProcessor
import numpy as np

class MyCustomProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("MyCustomProcessor")
    
    def initialize(self):
        # Load models, setup resources
        pass
    
    def process(self, frame: np.ndarray) -> np.ndarray:
        # Process frame
        return processed_frame
    
    def cleanup(self):
        # Release resources
        pass

# Usage
from app.pipeline.pipeline import Pipeline

pipeline = Pipeline("input_videos/exam.mp4")
pipeline.add_processor(MyCustomProcessor())
pipeline.run()
```

## Configuration

Edit `app/config/settings.py` to customize:
- Directory paths
- Supported video extensions
- Default codec
- Logging levels
- Processing settings

## Logging

Logs are written to:
- Console (stdout)
- `logs/` directory with timestamp

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Error Handling

The pipeline handles:
- Missing video files
- Invalid file extensions
- Corrupted video files
- Empty videos
- Output write failures
- Processor initialization failures

## Dependencies

- opencv-python >= 4.8.0
- numpy >= 1.24.0
- tqdm >= 4.65.0
- typing-extensions >= 4.5.0

## Design Principles

- **SOLID Principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Clean Architecture**: Separation of concerns, dependency injection
- **Modular Design**: Reusable components, no duplicated logic
- **Type Hints**: Full type annotations for better IDE support
- **Docstrings**: Comprehensive documentation for all modules
- **Error Handling**: Graceful degradation with meaningful errors

## Integration with FastAPI Backend

This module is designed to be called as a service from the FastAPI backend:

```python
# In FastAPI backend
from app.pipeline.pipeline import Pipeline

def process_video_endpoint(video_path: str):
    pipeline = Pipeline(video_path)
    metadata = pipeline.run()
    return metadata.to_dict()
```

## License

Part of the NeuroProctor AI-based Exam Cheating and Impersonation Detection project.

## Version

Current Version: 1.0.0 (Phase 1 - Infrastructure Only)
