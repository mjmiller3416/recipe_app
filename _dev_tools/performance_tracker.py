"""app/core/utils/performance.py

Performance logging utilities for tracking operation timing.
"""

from contextlib import contextmanager

# ── Imports ─────────────────────────────────────────────────────────────────────────────
import time
from typing import Optional

from _dev_tools import DebugLogger

@contextmanager
def log_performance(operation_name: str, log_level: str = "info", threshold_ms: Optional[float] = None):
    """
    Context manager for logging operation performance.

    Args:
        operation_name: Name of the operation being timed
        log_level: Log level to use ('debug', 'info', 'warning')
        threshold_ms: Optional threshold - only log if operation exceeds this time in ms

    Usage:
        with log_performance("Recipe database query"):
            results = expensive_database_operation()
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Only log if threshold not set or exceeded
        if threshold_ms is None or duration_ms >= threshold_ms:
            if duration_ms >= 1000:  # >= 1 second
                duration_str = f"{duration:.3f}s"
            else:
                duration_str = f"{duration_ms:.1f}ms"

            DebugLogger.log(f"{operation_name} completed in {duration_str}", log_level)


def log_slow_operation(operation_name: str, duration_s: float, threshold_s: float = 1.0):
    """
    Log slow operations that exceed a threshold.

    Args:
        operation_name: Name of the operation
        duration_s: Duration in seconds
        threshold_s: Threshold in seconds (default 1.0s)
    """
    if duration_s >= threshold_s:
        level = "warning" if duration_s >= 2.0 else "info"
        DebugLogger.log(f"Slow operation detected: {operation_name} took {duration_s:.3f}s", level)


class PerformanceTracker:
    """Simple performance tracker for measuring cumulative operations."""

    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.total_time = 0.0
        self.operation_count = 0

    def start(self):
        """Start timing an operation."""
        self.start_time = time.time()

    def stop(self):
        """Stop timing and add to total."""
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.total_time += duration
            self.operation_count += 1
            self.start_time = None
            return duration
        return 0.0

    def log_summary(self, log_level: str = "info"):
        """Log performance summary."""
        if self.operation_count > 0:
            avg_time = self.total_time / self.operation_count
            DebugLogger.log(
                f"{self.name} summary: {self.operation_count} operations, "
                f"total: {self.total_time:.3f}s, average: {avg_time:.3f}s",
                log_level
            )
