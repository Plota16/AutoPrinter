import logging
import sys
from pathlib import Path

def setup_logger(
        log_level: str = "INFO",
        log_dir: str = "logs",
        log_file: str = "auto_printer.log"
) -> logging.Logger:
    """
    Setup logger that logs to both console and file
    Deletes existing log file on each run

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        log_file: Log file name
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Full path to log file
    log_file_path = log_path / log_file

    # Delete existing log file
    if log_file_path.exists():
        log_file_path.unlink()

    # Create logger
    logger = logging.getLogger("auto_printer")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # Remove existing handlers

    # Console Handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # File Handler - DEBUG and above (no rotation needed)
    file_handler = logging.FileHandler(
        log_file_path,
        mode='w',  # 'w' mode overwrites the file
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log startup info
    logger.info("=" * 80)
    logger.info("Auto Printer Application Started")
    logger.info(f"Console Log Level: {log_level}")
    logger.info(f"File Log Level: DEBUG")
    logger.info(f"Log File: {log_file_path.resolve()}")
    logger.info("=" * 80)

    return logger

logger = setup_logger(log_level="DEBUG")

def get_logger(name: str = "auto_printer") -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)