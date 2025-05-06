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
        self._cache: dict[str, str] = {}  # 🔹 Caches already-loaded QSS content

    def load(self, qss_file_path: str) -> str:
        """
        Load and return a QSS file with theme variables injected.

        Args:
            qss_file_path (str): Path to the QSS file.

        Returns:
            str: QSS content with placeholders replaced by themed values.
        """
        if qss_file_path in self._cache:
            return self._cache[qss_file_path]

        try:
            raw_qss = Path(qss_file_path).read_text(encoding="utf-8")
            DebugLogger.log(f"[Loader] Opening QSS: {qss_file_path}", "debug")

            for key, value in self.theme.items():
                if key in NON_QSS_KEYS:
                    continue
                if not isinstance(value, str):
                    DebugLogger.log(f"[ThemedStyleLoader] ⚠️ Skipped non-str key: {key} → {type(value).__name__}", "warning")
                    continue
                raw_qss = raw_qss.replace(f"{{{key}}}", value)

            self._cache[qss_file_path] = raw_qss  # ✅ Cache result
            return raw_qss

        except FileNotFoundError:
            DebugLogger.log(f"[ThemedStyleLoader] QSS file not found: {qss_file_path}", "error")
            return ""
        except Exception as e:
            DebugLogger.log(f"[ThemedStyleLoader] Failed to load QSS: {e}", "error")
            return ""