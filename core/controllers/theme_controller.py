"""core/controllers/theme_controller.py

ThemeController class for managing application themes and stylesheets.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import json
from pathlib import Path

from PySide6.QtWidgets import QApplication

from config.paths.app_paths import AppPaths
from config.paths.qss_paths import QssPaths
from core.helpers.debug_logger import DebugLogger
from core.helpers.fontkit import register_all_fonts
from ui.styles.themes.dark_theme import THEME as DARK_THEME
from ui.styles.themes.light_theme import THEME as LIGHT_THEME
from ui.styles.utils.qss_combiner import QssCombiner
from ui.styles.utils.qss_loader import ThemedStyleLoader

# ── Constants ───────────────────────────────────────────────────────────────────
CONFIG_PATH = AppPaths.THEME_CONFIG_PATH
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Class Definition ────────────────────────────────────────────────────────────
class ThemeController:
    """
    Controls application-wide theme state and applies QSS styling.
    """

    def __init__(self):
        register_all_fonts()

        self.available_themes = {
            "dark": DARK_THEME,
            "light": LIGHT_THEME
        }
        self.current_theme_name = "dark"
        self.current_theme = DARK_THEME
        self.loader = ThemedStyleLoader(self.current_theme)

        self.load_user_theme()

    def apply_theme(self, view_qss_path: str = QssPaths.APPLICATION):
        """
        Load and apply the themed QSS to the running application.

        Args:
            view_qss_path (str): Optional additional stylesheet to load after base.qss.
        """
        app = QApplication.instance()
        if not app:
            return

        qss = (
            self.loader.load(QssPaths.APPLICATION) +
            self.loader.load(view_qss_path)
        )
        app.setStyleSheet(qss)

    def apply_theme_from_view(self, view_name: str):
        """
        Dynamically load and apply stylesheets associated with a given view.

        Args:
            view_name (str): The view name key for QssCombiner.
        """
        app = QApplication.instance()
        if not app:
            return

        qss = "".join(self.loader.load(path) for path in QssCombiner.get_for_view(view_name))
        app.setStyleSheet(qss)

    def set_theme(self, theme_name: str, view_qss_path: str = QssPaths.APPLICATION):
        """
        Set and apply a new theme.

        Args:
            theme_name (str): Either "dark" or "light"
            view_qss_path (str): Optional stylesheet to reapply with the theme
        """
        if theme_name not in self.available_themes:
            DebugLogger.log(f"Unknown theme '{theme_name}'", "error")
            return

        self.current_theme_name = theme_name
        self.current_theme = self.available_themes[theme_name]
        self.loader = ThemedStyleLoader(self.current_theme)

        self.save_user_theme()
        self.apply_theme(view_qss_path)

    def save_user_theme(self):
        """Persist selected theme name to disk."""
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"theme": self.current_theme_name}, f)
        except Exception as e:
            DebugLogger.log(f"Failed to save theme config: {e}", "error")

    def load_user_theme(self):
        """Load previously selected theme from disk, if available."""
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    saved_theme = data.get("theme", "dark")
                    self.set_theme(saved_theme)
            except Exception as e:
                DebugLogger.log(f"Failed to load saved theme: {e}", "error")

    def get_current_palette(self):
        """Return the current theme dict for use elsewhere."""
        return self.current_theme

    def refresh_styles(self, view_name: str = "dashboard"):
        """Reapply current theme for the given view."""
        self.loader = ThemedStyleLoader(self.current_theme)
        self.apply_theme_from_view(view_name)

