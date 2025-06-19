#!/usr/bin/env python3
"""
Advanced Logging System with Multiple Outputs and Structured Logging

This module provides a comprehensive logging solution with:
- Console and file output
- JSON structured logging
- Log rotation
- Different log levels
- Correlation IDs for request tracking
- Performance metrics
- Error handling with context
"""

import logging
import logging.handlers
import json
import time
import uuid
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
import threading
from dataclasses import dataclass, asdict


@dataclass
class LogContext:
    """Context information for structured logging"""
    correlation_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    service_name: str = "logging-service"
    version: str = "1.0.0"


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs
    Includes timestamp, level, message, and context information
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add context if available
        if hasattr(record, 'context'):
            log_entry["context"] = asdict(record.context)
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_entry["correlation_id"] = record.correlation_id
            
        # Add performance metrics if available
        if hasattr(record, 'duration'):
            log_entry["duration_ms"] = record.duration
            
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'exc_info', 'exc_text', 
                          'stack_info', 'context', 'correlation_id', 'duration']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable formatter for console output
    Includes colors for different log levels
    """
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m'  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color if stdout is a terminal
        if sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, '')
            reset = self.RESET
        else:
            color = reset = ''
            
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Base format
        formatted = f"{color}[{timestamp}] {record.levelname:8} {record.name}: {record.getMessage()}{reset}"
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            formatted += f" [ID: {record.correlation_id[:8]}]"
            
        # Add duration if available
        if hasattr(record, 'duration'):
            formatted += f" [{record.duration:.2f}ms]"
            
        return formatted


class AdvancedLogger:
    """
    Advanced logging system with multiple outputs and structured logging
    
    Features:
    - Multiple handlers (console, file, rotating file)
    - Structured JSON logging for files
    - Human-readable console output
    - Context management for correlation IDs
    - Performance timing
    - Error handling with context
    """
    
    def __init__(self, name: str = "app", log_level: str = "INFO", 
                 log_dir: str = "logs", max_file_size: int = 10485760,  # 10MB
                 backup_count: int = 5):
        """
        Initialize the logging system
        
        Args:
            name: Logger name
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            max_file_size: Maximum size of log files before rotation (bytes)
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Thread-local storage for context
        self._context = threading.local()
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up handlers
        self._setup_handlers(max_file_size, backup_count)
        
    def _setup_handlers(self, max_file_size: int, backup_count: int):
        """Set up different log handlers"""
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(ConsoleFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler for all logs (JSON format)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, f"{self.name}.log"),
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # Error file handler (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, f"{self.name}_errors.log"),
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
    def set_context(self, context: LogContext):
        """Set logging context for current thread"""
        self._context.current = context
        
    def get_context(self) -> Optional[LogContext]:
        """Get current logging context"""
        return getattr(self._context, 'current', None)
        
    def clear_context(self):
        """Clear current logging context"""
        if hasattr(self._context, 'current'):
            delattr(self._context, 'current')
            
    @contextmanager
    def context(self, **kwargs):
        """Context manager for temporary logging context"""
        # Generate correlation ID if not provided
        if 'correlation_id' not in kwargs:
            kwargs['correlation_id'] = str(uuid.uuid4())
            
        old_context = self.get_context()
        new_context = LogContext(**kwargs)
        
        try:
            self.set_context(new_context)
            yield new_context.correlation_id
        finally:
            if old_context:
                self.set_context(old_context)
            else:
                self.clear_context()
                
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Internal method to log with context"""
        # Create log record
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        # Add context if available
        context = self.get_context()
        if context:
            record.context = context
            record.correlation_id = context.correlation_id
            
        # Add extra fields
        for key, value in kwargs.items():
            setattr(record, key, value)
            
        # Handle the record
        self.logger.handle(record)
        
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception"""
        if exception:
            # Create record with exception info
            record = self.logger.makeRecord(
                name=self.logger.name,
                level=logging.ERROR,
                fn="",
                lno=0,
                msg=message,
                args=(),
                exc_info=(type(exception), exception, exception.__traceback__)
            )
        else:
            record = self.logger.makeRecord(
                name=self.logger.name,
                level=logging.ERROR,
                fn="",
                lno=0,
                msg=message,
                args=(),
                exc_info=None
            )
            
        # Add context if available
        context = self.get_context()
        if context:
            record.context = context
            record.correlation_id = context.correlation_id
            
        # Add extra fields
        for key, value in kwargs.items():
            setattr(record, key, value)
            
        # Handle the record
        self.logger.handle(record)
        
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
        
    @contextmanager
    def timer(self, operation_name: str):
        """Context manager for timing operations"""
        start_time = time.time()
        correlation_id = None
        
        try:
            # Get correlation ID from context if available
            context = self.get_context()
            if context:
                correlation_id = context.correlation_id
                
            self.info(f"Starting {operation_name}", operation=operation_name)
            yield
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.error(f"Failed {operation_name}", exception=e, 
                      operation=operation_name, duration=duration)
            raise
        else:
            duration = (time.time() - start_time) * 1000
            self.info(f"Completed {operation_name}", 
                     operation=operation_name, duration=duration)


# Singleton instance for easy access
_default_logger = None

def get_logger(name: str = "app", **kwargs) -> AdvancedLogger:
    """Get or create logger instance"""
    global _default_logger
    if _default_logger is None or _default_logger.name != name:
        _default_logger = AdvancedLogger(name, **kwargs)
    return _default_logger


# Example usage and testing
if __name__ == "__main__":
    # Initialize logger
    logger = get_logger("demo", log_level="DEBUG")
    
    # Basic logging
    logger.info("Application starting up")
    logger.debug("Debug information", component="startup", version="1.0.0")
    
    # Context-based logging
    with logger.context(user_id="user123", session_id="sess456") as correlation_id:
        logger.info("User logged in", action="login")
        
        # Nested operations
        with logger.timer("database_query"):
            time.sleep(0.1)  # Simulate work
            logger.info("Query executed", query="SELECT * FROM users", rows=42)
            
        # Error handling
        try:
            raise ValueError("Something went wrong")
        except Exception as e:
            logger.error("Operation failed", exception=e, user_action="data_processing")
    
    # Performance monitoring
    with logger.timer("api_call"):
        time.sleep(0.05)  # Simulate API call
        
    logger.info("Application ready", port=8080, environment="development")
    logger.warning("High memory usage detected", memory_usage="85%")
    logger.critical("Database connection lost", database="primary")
    
    print(f"\nLogs written to: {logger.log_dir}")
    print("Check the log files for structured JSON output!")