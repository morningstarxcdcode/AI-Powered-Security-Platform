import logging
import os
from logging.handlers import RotatingFileHandler

# Define the log file path relative to the project root
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scout.log'))

def setup_logger(name='scout', log_file=LOG_FILE, level=logging.INFO):
    """
    Set up a logger that writes to a rotating file and the console.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding handlers multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a rotating file handler
    # 1MB per file, keeping 5 backup files
    file_handler = RotatingFileHandler(log_file, maxBytes=1*1024*1024, backupCount=5)
    file_handler.setLevel(level)

    # Create a console handler to show important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only show warnings and above on console

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create a default logger instance to be used across the application
logger = setup_logger()

def log_error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def log_warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def log_info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def log_debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def log_exception(msg, *args, **kwargs):
    """Logs a message with exception information."""
    logger.exception(msg, *args, **kwargs)
