"""app/ui/views/settings.py

Settings view with category-based configuration interface.
Supports AI Image Generation settings and extensible for future categories.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from app.core.services.settings_service import SettingsService
from app.ui.views.base import BaseView


class Settings(BaseView):
    """Main Settings view with category selection and management."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Settings")

        # Settings data
        self.settings_service = SettingsService()

        self._build_ui()

    def _build_ui(self):
        """Build the main settings interface."""
        pass
