"""
Complete Logger - Captures ALL CLI output to both console and log file

This logger solves the issue where CLI output (banners, formatted text, progress
indicators) is printed via print() statements and not captured in log files.

Usage:
    with CompleteLogger(log_file_path) as logger:
        # All print() statements and logger calls are captured
        print("This goes to both console and log file")
        logger.info("This also goes to both")
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO


class CompleteLogger:
    """
    Context manager that captures ALL stdout to both console and log file.

    Combines Python logging with stdout redirection to ensure complete capture
    of all CLI output including print() statements, banners, and formatted text.
    """

    def __init__(self, log_file_path: Path, command: str = ""):
        """
        Initialize complete logger

        Args:
            log_file_path: Path to log file
            command: Command name (for logger identification)
        """
        self.log_file_path = Path(log_file_path)
        self.command = command or "agentic-docs"

        # Ensure log directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # File handle for logging
        self.log_file: Optional[TextIO] = None

        # Original stdout
        self.original_stdout = sys.stdout

        # Python logger for structured logging
        self.logger = logging.getLogger(self.command)
        self.logger.setLevel(logging.DEBUG)

        # Remove any existing handlers
        self.logger.handlers = []

    def __enter__(self):
        """Enter context - start capturing output"""
        # Open log file
        self.log_file = open(self.log_file_path, 'w', encoding='utf-8', buffering=1)

        # Add file handler to logger
        file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Redirect stdout to custom writer
        sys.stdout = TeeWriter(self.original_stdout, self.log_file)

        # Log initialization
        self.logger.info(f"Logging started: {self.log_file_path}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore stdout and close log file"""
        # Restore original stdout
        sys.stdout = self.original_stdout

        # Close log file
        if self.log_file:
            self.log_file.flush()
            self.log_file.close()

        # Log completion
        if exc_type is None:
            self.logger.info(f"Logging completed: {self.log_file_path}")
        else:
            self.logger.error(f"Logging ended with error: {exc_val}")

        # Don't suppress exceptions
        return False

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)


class TeeWriter:
    """
    Writes to multiple streams simultaneously (like Unix 'tee' command).

    This captures all print() output to both console and log file.
    """

    def __init__(self, *streams):
        """
        Initialize tee writer

        Args:
            *streams: File-like objects to write to
        """
        self.streams = streams

    def write(self, text):
        """Write text to all streams"""
        for stream in self.streams:
            try:
                stream.write(text)
                stream.flush()
            except Exception:
                # If one stream fails, continue with others
                pass

    def flush(self):
        """Flush all streams"""
        for stream in self.streams:
            try:
                stream.flush()
            except Exception:
                pass

    def isatty(self):
        """Check if any stream is a tty"""
        return any(hasattr(s, 'isatty') and s.isatty() for s in self.streams)


def create_complete_logger(command: str, log_dir: Optional[Path] = None) -> CompleteLogger:
    """
    Create a complete logger instance

    Args:
        command: Command name (e.g., 'agentic-docs:validate')
        log_dir: Optional log directory (defaults to ./logs)

    Returns:
        CompleteLogger instance (use as context manager)
    """
    if log_dir is None:
        log_dir = Path("logs")

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    safe_command = command.replace(":", "-").replace("/", "-")
    log_file = log_dir / f"{safe_command}-{timestamp}.log"

    return CompleteLogger(log_file, command)
