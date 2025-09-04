"""app/core/dev_tools/test_harness.py

This module provides a test harness for launching custom widget test files.
Prompts the user for a test module name, imports it, and runs its `run_test()` function.
"""


import importlib

# ── Imports ─────────────────────────────────────────────────────────────────────────────
import sys

from . import DebugLogger

# ── Class Definition ────────────────────────────────────────────────────────────────────
class TestHarness:
    """Test harness for launching custom widget test files."""

    @staticmethod
    def launch_from_test_file(app) -> None:
        """Prompts for a test module and runs its `run_test()` function."""
        print("🔧 Dev Test Harness\n")
        test_name = input("🔹 Enter test file name (e.g. test_combobox):\n> ").strip()

        module_path = f"tests.dev.{test_name}"
        try:
            module = importlib.import_module(module_path)

            if not hasattr(module, "run_test"):
                DebugLogger.log(f"❌ `{module_path}` has no `run_test(app)` function.", "error")
                return

            window = module.run_test(app)
            window.setWindowTitle(f"Test: {test_name}")
            window.show()

            DebugLogger.log(f"🧪 Running: {module_path}.run_test()", "info")

        except ModuleNotFoundError as e:
            DebugLogger.log(f"❌ Test file not found: {module_path}", "error")
            DebugLogger.log(f"{type(e).__name__}: {e}", "error")
