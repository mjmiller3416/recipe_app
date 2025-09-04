"""app/core/utils/startup_timer.py

Utility class for measuring and logging elapsed time during application startup.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import logging
import time

from _dev_tools import DebugLogger

# ── Logger Setup ─────────────────────────────────────────────────────────────────────────────
log = logging.getLogger(__name__)
_startup_start_time = time.perf_counter()


# ── Startup Timer ────────────────────────────────────────────────────────────────────────────
class StartupTimer:
    """Utility for measuring time taken to initialize parts of the application."""

    def __init__(self, label: str):
        self.label = label
        self.start_time = time.perf_counter()
        DebugLogger.log(f"[StartupTimer.__init__] [TIMER] [{self.label}] Started.")

    def checkpoint(self, msg: str):
        elapsed = time.perf_counter() - self.start_time
        DebugLogger.log(f"[StartupTimer.checkpoint] [TIMER] [{self.label}] {msg}: {elapsed:.3f}s")

    @staticmethod
    def summary(label: str = "Startup Complete"):
        if _startup_start_time is None:
            DebugLogger.log("[StartupTimer.summary] Called before import!")
            return
        total = time.perf_counter() - _startup_start_time
        DebugLogger.log(f"{label} took [{total:.3f}s]")
