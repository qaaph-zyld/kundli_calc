import logging
import sys
from typing import Any, Dict

from .config import settings

def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

def log_request(logger: logging.Logger, request_data: Dict[str, Any]) -> None:
    """Log incoming request data."""
    logger.info(f"Received request: {request_data}")

def log_response(logger: logging.Logger, response_data: Dict[str, Any]) -> None:
    """Log outgoing response data."""
    logger.info(f"Sending response: {response_data}")

def log_error(logger: logging.Logger, error: Exception) -> None:
    """Log error details."""
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
