"""app/ui/views/settings/_base_category.py

Base class for settings category widgets.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from abc import abstractmethod
from typing import Any, Dict

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.core.services.settings_service import SettingsService


class BaseSettingsCategory(QWidget):
    """Base class for all settings category widgets."""

    # Signal emitted when settings in this category change
    settings_changed = Signal(str, dict)  # category_name, changed_values

    def __init__(self, category_name: str, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.settings_service = SettingsService()

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

        self._build_ui()
        self._load_settings()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Build the UI for this settings category."""
        raise NotImplementedError("Subclasses must implement _build_ui")

    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        raise NotImplementedError("Subclasses must implement _connect_signals")

    def _load_settings(self) -> None:
        """Load current settings into the UI."""
        raise NotImplementedError("Subclasses must implement _load_settings")

    def _save_settings(self) -> None:
        """Save current UI values to settings."""
        raise NotImplementedError("Subclasses must implement _save_settings")

    def get_changed_values(self) -> Dict[str, Any]:
        """Get dict of values that have changed from defaults."""
        raise NotImplementedError("Subclasses must implement get_changed_values")

    def reset_category(self) -> bool:
        """Reset this category to default values."""
        success = self.settings_service.reset_to_defaults(self.category_name)
        if success:
            self._load_settings()
        return success

    def save_category(self) -> bool:
        """Save the current category settings."""
        try:
            self._save_settings()
            return True
        except Exception as e:
            from _dev_tools import DebugLogger
            DebugLogger.log(f"Error saving {self.category_name} settings: {e}", "error")
            return False

    def _emit_settings_changed(self) -> None:
        """Emit signal when settings change."""
        changed_values = self.get_changed_values()
        if changed_values:
            self.settings_changed.emit(self.category_name, changed_values)