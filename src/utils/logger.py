"""
ADCC Analysis Engine v0.6 - Logging Utilities
Centralized logging configuration and utilities.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import structlog

from core.constants import LOGS_DIR, LOG_LEVEL, LOG_RETENTION_DAYS


def setup_logging(
    log_level: Optional[str] = None,
    log_dir: Optional[Path] = None
) -> None:
    """
    Setup structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
    """
    # Use defaults if not provided
    log_level = log_level or LOG_LEVEL
    log_dir = log_dir or LOGS_DIR
    
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Setup file handlers
    system_handler = logging.handlers.RotatingFileHandler(
        log_dir / "system.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    debug_handler = logging.handlers.RotatingFileHandler(
        log_dir / "debug.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    audit_handler = logging.handlers.RotatingFileHandler(
        log_dir / "audit.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # Apply formatters
    system_handler.setFormatter(file_formatter)
    debug_handler.setFormatter(file_formatter)
    audit_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Add handlers
    root_logger.addHandler(system_handler)
    root_logger.addHandler(console_handler)
    
    # Setup debug logger
    debug_logger = logging.getLogger("debug")
    debug_logger.setLevel(logging.DEBUG)
    debug_logger.addHandler(debug_handler)
    
    # Setup audit logger
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name) 