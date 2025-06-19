"""style_manager/loaders/theme_loader.py

Centralized QSS loading utility that injects theme variables into QSS files.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from app.core.utils import DebugLogger

# ── Constants ───────────────────────────────────────────────────────────────────
NON_QSS_KEYS = {"ICON_STYLES"}  # skip injecting these into QSS


# ── Class Definition ────────────────────────────────────────────────────────────
class ThemeLoader:
    """
    Loads a QSS file and injects theme variables before returning the final string.
    Theme values are passed as a dictionary and replace {PLACEHOLDER} tags.
    """

    def __init__(self, theme: dict):
        self.theme = theme
        self._cache: dict[str, str] = {}  # cache for loaded QSS files

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

            injected_count = 0
            for key, value in self.theme.items():
                if key in NON_QSS_KEYS:
                    continue
                if not isinstance(value, str):
                    DebugLogger.log(f"[ThemeLoader] ⚠️ Skipped non-str key: {key} → {type(value).__name__}", "warning")
                    continue

                placeholder = f"{{{key}}}"
                if placeholder in raw_qss:
                    DebugLogger.log("[ThemeLoader] Injecting: {placeholder} → {value}", "debug")
                    raw_qss = raw_qss.replace(placeholder, value)
                    injected_count += 1

            if injected_count > 0:
                DebugLogger.log(
                    f"[ThemeLoader] Completed injection for {qss_file_path} ({injected_count} keys replaced)\n",
                    "info"
                )
            self._cache[qss_file_path] = raw_qss
            return raw_qss

        except FileNotFoundError:
            DebugLogger.log(f"[ThemeLoader] QSS file not found: {qss_file_path}", "error")
            return ""
        except Exception as e:
            DebugLogger.log(f"[ThemeLoader] Failed to load QSS: {e}", "error")
            return ""
