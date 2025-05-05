"""
ui/styles/utils/qss_loader.py

Provides the ThemedStyleLoader class, which loads Qt Stylesheet (.qss) files and injects dynamic theme 
variables into them at runtime. Used by ThemeController to support theme switching and consistent application 
styling across views and components.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from core.helpers import DebugLogger

# ── Constants ───────────────────────────────────────────────────────────────────
NON_QSS_KEYS = {"ICON_STYLES"}  # Skip injecting these into QSS


# ── Class Definition ────────────────────────────────────────────────────────────
class ThemedStyleLoader:
    """
    Loads a QSS file and injects theme variables before returning the final string.
    Theme values are passed as a dictionary and replace {PLACEHOLDER} tags.
    """

    def __init__(self, theme: dict):
        self.theme = theme

    def load(self, qss_file_path: str) -> str:
        """
        Load and return a QSS file with theme variables injected.

        Args:
            qss_file_path (str): Path to the QSS file.

        Returns:
            str: QSS content with placeholders replaced by themed values.
        """
        try:
            with open(qss_file_path, "r", encoding="utf-8") as f:
                raw_qss = f.read()

                for key, value in self.theme.items():
                    if key in NON_QSS_KEYS:
                        continue
                    if not isinstance(value, str):
                        DebugLogger.log(f"[ThemedStyleLoader] ⚠️ Skipped non-str key: {key} → {type(value).__name__}", "warning")
                        continue
                    raw_qss = raw_qss.replace(f"{{{key}}}", value)

                return raw_qss

        except FileNotFoundError:
            DebugLogger.log(f"[ThemedStyleLoader] QSS file not found: {qss_file_path}", "error")
            return ""
        except Exception as e:
            DebugLogger.log(f"[ThemedStyleLoader] Failed to load QSS: {e}", "error")
            return ""
