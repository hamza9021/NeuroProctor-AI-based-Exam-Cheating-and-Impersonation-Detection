"""
Logging utilities for AI Services module.

This module provides structured logging functionality with both
console and file output capabilities.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.config.settings import settings


class Logger:
    """Custom logger for AI Services pipeline."""

    def __init__(self, name: str, log_file: Optional[str] = None):
        """
        Initialize logger with console and file handlers.

        Args:
            name: Logger name (typically module name)
            log_file: Optional log file name. If not provided, auto-generates based on timestamp.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))

        # Avoid adding duplicate handlers
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
            console_formatter = logging.Formatter(
                settings.LOG_FORMAT, settings.LOG_DATE_FORMAT
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # File handler
            if log_file is None:
                log_file = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            # Ensure log directory exists
            settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
            
            log_path = settings.LOG_DIR / log_file
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
            file_formatter = logging.Formatter(
                settings.LOG_FORMAT, settings.LOG_DATE_FORMAT
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)


def get_logger(name: str, log_file: Optional[str] = None) -> Logger:
    """
    Factory function to create or retrieve a logger instance.

    Args:
        name: Logger name
        log_file: Optional log file name

    Returns:
        Logger instance
    """
    return Logger(name, log_file)
