#!/usr/bin/env python3
"""Test application demonstrating all features of DebugLogger."""

import os
import sys
# ensure project root on path for dev_tools import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dev_tools.debug_logger import DebugLogger


def print_divider(title: str) -> None:
    print("\n" + "=" * 20 + f" {title} " + "=" * 20)


class TestClass:
    def __init__(self, value: int):
        self.value = value

    def do_something(self, tv):
        DebugLogger.log(
            "Inside {self.__class__.__name__}.do_something with tv={tv}", "info"
        )
        DebugLogger.log("Bracket example: [TEST]", "debug")


def main():
    log_file = "debug_test.log"
    # Cleanup existing log file
    if os.path.exists(log_file):
        os.remove(log_file)

    # 1. Default logging at DEBUG level
    print_divider("Default Logging (DEBUG)")
    DebugLogger.enable(True)
    DebugLogger.set_log_level("DEBUG")
    DebugLogger.log("Debug message visible", "debug")
    DebugLogger.log("Info message visible", "info")
    DebugLogger.log("Warning message visible", "warning")

    # 2. Log level filtering
    print_divider("Log Level Filtering (WARNING)")
    DebugLogger.set_log_level("WARNING")
    DebugLogger.log("This DEBUG should NOT appear", "debug")
    DebugLogger.log("This INFO should NOT appear", "info")
    DebugLogger.log("This WARNING should appear", "warning")
    DebugLogger.log("This ERROR should appear", "error")

    # 3. Variable injection and context resolution
    print_divider("Variable Injection & Context")
    test_var = 42
    tc = TestClass(test_var)
    DebugLogger.set_log_level("INFO")
    tc.do_something(test_var)

    # 4. Bracket highlighting demonstration
    print_divider("Bracket Highlighting")
    DebugLogger.set_log_level("DEBUG")
    DebugLogger.log("Bracket highlight: [HIGHLIGHT] and [INFO]", "info")

    # 5. log_and_raise demonstration
    print_divider("log_and_raise Demo")
    try:
        DebugLogger.log_and_raise("This triggers an exception", ValueError)
    except ValueError as e:
        print(f"Caught exception: {e}")

    # 6. File logging (ANSI codes stripped)
    print_divider("File Logging to debug_test.log")
    DebugLogger.set_log_file(log_file)
    DebugLogger.set_log_level("DEBUG")
    DebugLogger.log("Logging to file with var={test_var}", "info")
    DebugLogger.log("Another error to file", "error")
    print(f"Contents of log file ({DebugLogger._log_file_path}):")
    with open(DebugLogger._log_file_path, "r") as f:
        print(f.read().rstrip())

    # 7. Disabling logging
    print_divider("Disabling Logging")
    DebugLogger.enable(False)
    DebugLogger.log("This should NOT appear anywhere", "info")
    print("Logging disabled; no more messages should appear.")


if __name__ == "__main__":
    main()
