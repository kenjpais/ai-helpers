"""
Logger - Structured logging with CLI output and timestamped log files

Based on REFACTOR_MAY_8.md requirements for comprehensive logging.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class AgenticLogger:
    """Logger for agentic-docs commands"""

    def __init__(self, command: str, log_dir: Path = Path("logs")):
        """
        Initialize logger

        Args:
            command: Command name (e.g., 'agentic-docs:create')
            log_dir: Directory for log files
        """
        self.command = command
        self.log_dir = log_dir
        self.log_file: Optional[Path] = None

        # Create logs directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        safe_command = command.replace(":", "-").replace("/", "-")
        self.log_file = self.log_dir / f"{safe_command}-{timestamp}.log"

        # Configure Python logging
        self.logger = logging.getLogger(command)
        self.logger.setLevel(logging.INFO)

        # File handler (detailed)
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler (simplified)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)

    def info(self, message: str, cli_only: bool = False):
        """Log info message"""
        if cli_only:
            print(message)
        else:
            self.logger.info(message)

    def debug(self, message: str):
        """Log debug message (file only)"""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def log_start(self, repo_path: str):
        """Log command start"""
        self.info(f"Command invoked: /{self.command}")
        self.info(f"Repository: {repo_path}")
        self.info(f"Timestamp: {datetime.now().isoformat()}")
        self.info(f"Log file: {self.log_file}")

    def log_phase(self, phase_name: str, status: str = "STARTED"):
        """Log phase transition"""
        self.info(f"Phase: {phase_name} - {status}")

    def log_tool_use(self, tool_name: str, details: str = ""):
        """Log tool usage"""
        msg = f"Tool: {tool_name}"
        if details:
            msg += f" - {details}"
        self.debug(msg)

    def log_skill_invocation(self, skill_name: str):
        """Log skill invocation"""
        self.info(f"Skill invoked: {skill_name}")

    def log_data_source(self, source: str):
        """Log data source"""
        self.info(f"Data source: {source}")

    def log_file_creation(self, file_path: str):
        """Log file creation"""
        self.info(f"Created: {file_path}")

    def log_completion(self, duration_formatted: str):
        """Log command completion"""
        self.info("")
        self.info(f"Execution completed successfully")
        self.info(f"Total duration: {duration_formatted}")
        self.info(f"Log file: {self.log_file}")

    def print_banner(self, title: str, emoji: str = "🚀"):
        """Print CLI banner"""
        print()
        print(f"{emoji} {title}")
        print("=" * 60)

    def print_section(self, title: str):
        """Print section header"""
        print()
        print(title)
        print("=" * 60)


def create_logger(command: str, log_dir: Optional[Path] = None) -> AgenticLogger:
    """
    Create a logger instance

    Args:
        command: Command name
        log_dir: Optional log directory (defaults to ./logs)

    Returns:
        AgenticLogger instance
    """
    if log_dir is None:
        log_dir = Path("logs")

    return AgenticLogger(command, log_dir)
