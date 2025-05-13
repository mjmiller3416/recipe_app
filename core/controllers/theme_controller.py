"""core/controllers/theme_controller.py

Singleton that owns the current palette and broadcasts changes.
"""

# ── Imports ────────────────────────────────────────────────────────────────
import json
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from config.paths.app_paths import AppPaths
from config.paths.qss_paths import QssPaths
from core.helpers.debug_logger import DebugLogger
from core.helpers.fontkit import register_all_fonts
from core.helpers.singleton_mixin import SingletonMixin
from ui.styles.themes.dark_theme import THEME as DARK_THEME
from ui.styles.themes.light_theme import THEME as LIGHT_THEME
from ui.styles.utils.qss_combiner import QssCombiner
from ui.styles.utils.qss_loader import ThemedStyleLoader
from ui.styles.utils.theme_utils import flatten_theme_dict

# ── Constants ─────────────────────────────────────────────────────────────
CONFIG_PATH = AppPaths.THEME_CONFIG_PATH

# ── Class ────────────────────────────────────────
class ThemeController(QObject, SingletonMixin):
    """
    Global palette manager. Emits `theme_changed(dict)` when the colours flip.
    Widgets listen via IconController; ThemeController never imports UI code.
    """

    theme_changed = Signal(dict) # palette

    def __init__(self) -> None:
        super().__init__() 
        # ensure config dir exists
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True) 
        register_all_fonts()

        # ── Load Themes ──
        self._themes: Dict[str, Dict] = {
            "dark":  flatten_theme_dict(DARK_THEME),
            "light": flatten_theme_dict(LIGHT_THEME),
        }
            
        # start with saved or default
        self._name: str   = "dark"
        self._palette: Dict = self._themes["dark"]
        self._loader = ThemedStyleLoader(self._palette)
           
    # ── Public Methods ────────────────────────────────────
    def get_current_palette(self) -> Dict:
        return self._palette

    def apply_full_theme(self) -> None:
        app = QApplication.instance()
        if not app:
            DebugLogger.log("No QApplication instance, skipping full QSS load.", "warning")
            return

        # ── Load QSS Files ──
        all_views = QssCombiner.get_all_styles()   # grabs every stylesheet exactly once

        loaded = [self._loader.load(path) for path in all_views]
        final_qss = "".join(loaded)
        app.setStyleSheet(final_qss)

        self.theme_changed.emit(self._palette)
        loaded_files = "\n  • ".join(all_views) + "\n"
        DebugLogger.log("[Theme] Full QSS applied. Loaded stylesheets:\n  • {loaded_files}", "info")
    # ── Private Methods ────────────────────────────────────

