"""
Timer utilities for AI Services module.

This module provides timing functionality for measuring processing
time and performance metrics.
"""

import time
from typing import Optional
from contextlib import contextmanager


class Timer:
    """Timer class for measuring execution time."""

    def __init__(self):
        """Initialize timer."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: float = 0.0

    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.time()
        self.end_time = None
        self.elapsed_time = 0.0

    def stop(self) -> float:
        """
        Stop the timer and return elapsed time.

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            raise RuntimeError("Timer has not been started")
        
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        return self.elapsed_time

    def reset(self) -> None:
        """Reset the timer."""
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0.0

    def get_elapsed(self) -> float:
        """
        Get elapsed time without stopping the timer.

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        
        current_time = time.time()
        return current_time - self.start_time

    def get_elapsed_formatted(self) -> str:
        """
        Get elapsed time formatted as string.

        Returns:
            Formatted elapsed time string
        """
        elapsed = self.get_elapsed()
        return self.format_time(elapsed)

    @staticmethod
    def format_time(seconds: float) -> str:
        """
        Format time in seconds to human-readable string.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.2f}h"


@contextmanager
def timer_context():
    """
    Context manager for timing code blocks.

    Yields:
        Timer instance

    Example:
        with timer_context() as timer:
            # Your code here
            pass
        print(f"Elapsed: {timer.get_elapsed_formatted()}")
    """
    timer = Timer()
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()
