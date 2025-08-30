"""
Logging configuration for the GUI Testing Tool
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import streamlit as st

class StreamlitLogHandler(logging.Handler):
    """Custom log handler that displays logs in Streamlit"""
    
    def emit(self, record):
        """Emit a log record to Streamlit"""
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                st.error(f"🚨 {msg}")
            elif record.levelno >= logging.WARNING:
                st.warning(f"⚠️ {msg}")
            elif record.levelno >= logging.INFO:
                st.info(f"ℹ️ {msg}")
            else:
                st.text(msg)
        except Exception:
            self.handleError(record)

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    include_streamlit: bool = True
) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        include_streamlit: Whether to include Streamlit log handler
        
    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger("gui_testing_tool")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Streamlit handler (if in Streamlit context)
    if include_streamlit:
        try:
            streamlit_handler = StreamlitLogHandler()
            streamlit_handler.setLevel(logging.INFO)
            streamlit_handler.setFormatter(
                logging.Formatter('%(levelname)s: %(message)s')
            )
            logger.addHandler(streamlit_handler)
        except Exception:
            # Streamlit not available, skip
            pass
    
    return logger

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("gui_testing_tool")
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper

def handle_error(error: Exception, context: str = "", show_in_ui: bool = True) -> None:
    """
    Handle errors with consistent logging and user feedback
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        show_in_ui: Whether to show the error in the Streamlit UI
    """
    logger = logging.getLogger("gui_testing_tool")
    
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)
    
    if show_in_ui:
        st.error(f"❌ {error_msg}")
        
        # Show details in expander for debugging
        with st.expander("🔍 Error Details"):
            st.code(str(error))
            if hasattr(error, '__traceback__'):
                import traceback
                st.text("Traceback:")
                st.code(traceback.format_exc())

class ErrorContext:
    """Context manager for error handling"""
    
    def __init__(self, context: str, show_in_ui: bool = True):
        self.context = context
        self.show_in_ui = show_in_ui
        self.logger = logging.getLogger("gui_testing_tool")
    
    def __enter__(self):
        self.logger.debug(f"Entering context: {self.context}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            handle_error(exc_val, self.context, self.show_in_ui)
            return False  # Don't suppress the exception
        
        self.logger.debug(f"Exiting context: {self.context}")
        return True

# Pre-configured logger instance
logger = setup_logging()