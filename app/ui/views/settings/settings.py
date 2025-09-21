"""app/ui/views/settings.py

Settings view with category-based configuration interface.
Supports AI Image Generation settings and extensible for future categories.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

from _dev_tools import DebugLogger
from app.core.services.ai_gen import ImageGenConfig, RecipeImageHelper
from app.core.services.settings_service import SettingsService
from app.style.icon import Icon
from app.ui.components.layout.card import Card
from app.ui.components.widgets import Button, ComboBox
from app.ui.views.base import BaseView


class SettingsCategory(Card):
    """Base class for settings categories."""

    settings_changed = Signal(str, dict)  # category_name, settings_dict

    def __init__(self, category_name: str, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.setObjectName(f"{category_name}Settings")

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings as dictionary. Override in subclasses."""
        return {}

    def set_settings(self, settings: Dict[str, Any]):
        """Apply settings from dictionary. Override in subclasses."""
        pass

    def validate_settings(self) -> bool:
        """Validate current settings. Override in subclasses."""
        return True


class Settings(BaseView):
    """Main Settings view with category selection and management."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Settings")

        # Settings data
        self.settings_service = SettingsService()
        self.categories: Dict[str, SettingsCategory] = {}

        self._build_ui()

    def _build_ui(self):
        """Build the main settings interface."""
        pass
