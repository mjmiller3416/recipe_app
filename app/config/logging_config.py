"""app/config/logging_config.py

Centralized logging configuration for different environments.
"""

import os

from _dev_tools import DebugLogger


class LoggingConfig:
    """Manages logging configuration for different environments."""

    # Environment-based log levels
    LOG_LEVELS = {
        'development': 'DEBUG',
        'testing': 'INFO',
        'staging': 'WARNING',
        'production': 'ERROR'
    }

    @classmethod
    def setup_logging(cls, environment: str = None, log_file: str = None):
        """
        Configure logging for the specified environment.

        Args:
            environment: 'development', 'testing', 'staging', or 'production'
            log_file: Optional log file path
        """
        # Default to development if not specified
        if environment is None:
            environment = os.getenv('APP_ENVIRONMENT', 'development')

        # Set log level based on environment
        log_level = cls.LOG_LEVELS.get(environment, 'INFO')
        DebugLogger.set_log_level(log_level)

        # Enable file logging if specified
        if log_file:
            DebugLogger.set_log_file(log_file)
        elif environment in ['staging', 'production']:
            # Auto-enable file logging for non-dev environments
            DebugLogger.set_log_file(f"recipe_app_{environment}.log")

        DebugLogger.log(f"Logging configured for {environment} environment at {log_level} level", "info")

    @classmethod
    def enable_debug_mode(cls):
        """Enable verbose debug logging."""
        DebugLogger.set_log_level('DEBUG')
        DebugLogger.log("Debug logging enabled", "info")

    @classmethod
    def enable_quiet_mode(cls):
        """Enable minimal logging (warnings and errors only)."""
        DebugLogger.set_log_level('WARNING')
        DebugLogger.log("Quiet logging mode enabled", "warning")

    @classmethod
    def disable_logging(cls):
        """Disable all logging output."""
        DebugLogger.enable(False)
