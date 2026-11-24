"""Logging configuration for NexusRAG.
Provides standard structured logging compatible with Cloud Run and local development.
"""
import logging
import sys
from pathlib import Path

_loggers = {}

def setup_logger(name: str = "nexusrag", log_file: Path = None, level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a named logger with console and optional file output."""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Avoid duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Standard out stream handler (vital for GCP Cloud Run / Cloud Logging)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Optional file handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger

def get_logger(name: str = "nexusrag") -> logging.Logger:
    """Returns an existing logger or creates one with defaults."""
    if name in _loggers:
        return _loggers[name]
    from ..config import LOGS_DIR
    return setup_logger(name, log_file=LOGS_DIR / "nexusrag.log")
