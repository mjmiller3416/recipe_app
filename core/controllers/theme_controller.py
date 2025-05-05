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

        self._load_user_theme()
        # initial QSS apply
        self.apply_theme()       
        
    # ── Public Methods ────────────────────────────────────
    def get_current_palette(self) -> Dict:
        return self._palette

    def set_theme(self, name: str, extra_sheet: str = QssPaths.APPLICATION) -> None:

        if name not in self._themes:
            DebugLogger.log(f"Unknown theme '{name}'", "error")
            return

        self._name = name
        self._palette = self._themes[name]
        self._loader = ThemedStyleLoader(self._palette)
        self._save_user_theme()
        self.apply_theme(extra_sheet)

    def apply_theme(self, view_sheet: Optional[str] = None) -> None:
       """Alias for backward compatibility. Calls the new internal logic."""
       self._apply_qss_and_emit(view_sheet)

    def _apply_qss_and_emit(self, view_sheet: Optional[str] = None) -> None:
        app = QApplication.instance()
        if not app:
            DebugLogger.log("No QApplication instance, skipping QSS apply.", "warning")
            return
        # combine global and view-specific QSS
        qss_parts = [self._loader.load(QssPaths.APPLICATION)]
        if view_sheet:
            qss_parts.append(self._loader.load(view_sheet))
        combined = "".join(qss_parts)
        app.setStyleSheet(combined)
        # notify icons and other listeners
        self.theme_changed.emit(self._palette)      

    def apply_theme_from_view(self, view: str) -> None:
        """Swap in the per-view bundle (called by your screen manager)."""
        app = QApplication.instance()
        if not app:
            return

        sheets = [self._loader.load(path) for path in QssCombiner.get_for_view(view)]
        app.setStyleSheet("".join(sheets))

    # ── Private Methods ────────────────────────────────────
    def _save_user_theme(self) -> None:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"theme": self._name}, f)
        except Exception as e:
            DebugLogger.log(f"Failed to save theme config: {e}", "error")

    def _load_user_theme(self) -> None:
        if not CONFIG_PATH.exists():
            return
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            name = data.get("theme")
            if name in self._themes:
                self._name = name
                self._palette = self._themes[name]
                self._loader = ThemedStyleLoader(self._palette)
        except Exception as e:
            DebugLogger.log(f"Loading saved theme failed: {e}", "error")
