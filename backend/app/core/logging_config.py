"""
Centralized logging configuration for the application.

This module provides a unified logging setup with:
- Rotating file handlers
- Console output
- Configurable log levels
- Separate error log file
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_level: str = "INFO",
    log_file_max_bytes: int = 10 * 1024 * 1024,  # 10MB
    log_file_backup_count: int = 5
) -> None:
    """
    Configure application logging with rotating file handlers and console output.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file_max_bytes: Maximum size of log file before rotation
        log_file_backup_count: Number of backup log files to keep
    """
    # Get the backend directory (parent of app directory)
    backend_dir = Path(__file__).parent.parent.parent
    logs_dir = backend_dir / 'logs'
    
    # Create logs directory if it doesn't exist
    logs_dir.mkdir(exist_ok=True)
    
    # Determine log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation (all logs)
    file_handler = RotatingFileHandler(
        logs_dir / 'app.log',
        maxBytes=log_file_max_bytes,
        backupCount=log_file_backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    
    # Error file handler (only errors and critical)
    error_handler = RotatingFileHandler(
        logs_dir / 'error.log',
        maxBytes=log_file_max_bytes,
        backupCount=log_file_backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(error_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Logging initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {logs_dir / 'app.log'}")
    logger.info(f"Error log: {logs_dir / 'error.log'}")
    logger.info("=" * 50)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Name of the module (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
