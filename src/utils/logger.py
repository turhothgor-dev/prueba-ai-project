"""Centralized logging configuration for MediaOrganizer."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    log_level: str = "DEBUG",
    log_dir: Path | None = None,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3,
) -> logging.Logger:
    """Set up centralized logging with console and file handlers.

    Configures logging with:
    - Console handler at INFO level
    - Rotating file handler at DEBUG level (5MB max, 3 backups)
    - Standardized format: %(asctime)s - %(name)s - %(levelname)s - %(message)s

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Defaults to "DEBUG".
        log_dir: Directory for log files. Defaults to ~/.mediaorganizer/logs/.
        max_bytes: Maximum size of each log file before rotation.
            Defaults to 5MB.
        backup_count: Number of backup log files to keep.
            Defaults to 3.

    Returns:
        Configured root logger instance.

    Example:
        >>> logger = setup_logging()
        >>> logger.info("Application started")
    """
    # Set default log directory
    if log_dir is None:
        log_dir = Path.home() / ".mediaorganizer" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "mediaorganizer.log"

    # Configure formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Get root logger
    root_logger = logging.getLogger("mediaorganizer")
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    # Remove existing handlers to avoid duplicates on re-initialization
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler (INFO level and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation (DEBUG level)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger under the 'mediaorganizer' namespace.

    Use this function instead of logging.getLogger() directly to ensure
    all loggers share the same configuration.

    Args:
        name: Logger name, typically __name__ of the module.

    Returns:
        Configured logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Module-specific debug message")
    """
    return logging.getLogger(f"mediaorganizer.{name}")


class LoggingMixin:
    """Mixin class to inject a configured logger into any class.

    Usage:
        class MyClass(LoggingMixin):
            def do_something(self):
                self.logger.info("Doing something")
    """

    @property
    def logger(self) -> logging.Logger:
        """Return a logger named after the class."""
        return get_logger(self.__class__.__name__)
