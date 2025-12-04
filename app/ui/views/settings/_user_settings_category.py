"""app/ui/views/settings/_user_settings_category.py

User settings category widget for managing username and profile settings.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.ui.components.layout.card import Card
from ._base_category import BaseSettingsCategory


class UserSettingsCategory(BaseSettingsCategory):
    """Settings category for user profile information."""

    def __init__(self, parent=None):
        self._original_username = ""
        self._username_input = None
        super().__init__("user", parent)

    def _build_ui(self) -> None:
        """Build the user settings UI."""
        # Username Section
        username_card = Card(card_type="Default")
        username_card.setHeader("Username")
        username_card.setSubHeader("Choose how you'd like to be identified in the application.")
        username_card.expandWidth(True)

        # Username input
        username_container = QWidget()
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(8)

        username_label = QLabel("Username")
        username_label.setObjectName("SettingsLabel")

        self._username_input = QLineEdit()
        self._username_input.setObjectName("SettingsInput")
        self._username_input.setPlaceholderText("Enter your username")
        self._username_input.setMaxLength(50)

        username_layout.addWidget(username_label)
        username_layout.addWidget(self._username_input)

        username_card.addWidget(username_container)
        self.layout.addWidget(username_card)

        # Add stretch to push content to top
        self.layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        if self._username_input:
            self._username_input.textChanged.connect(self._on_username_changed)

    def _load_settings(self) -> None:
        """Load current settings into the UI."""
        username = self.settings_service.get("user.username", "User")
        self._original_username = username

        if self._username_input:
            self._username_input.setText(username)

    def _save_settings(self) -> None:
        """Save current UI values to settings."""
        if self._username_input:
            username = self._username_input.text().strip() or "User"
            self.settings_service.set("user.username", username)
            self._original_username = username

            # Emit signal to update sidebar
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app and hasattr(app, 'main_window'):
                main_window = app.main_window
                if hasattr(main_window, 'sidebar'):
                    main_window.sidebar.update_username(username)

    def get_changed_values(self) -> Dict[str, Any]:
        """Get dict of values that have changed from defaults."""
        changes = {}

        if self._username_input:
            current_username = self._username_input.text().strip() or "User"
            if current_username != self._original_username:
                changes["username"] = current_username

        return changes

    def _on_username_changed(self) -> None:
        """Handle username input changes."""
        self._emit_settings_changed()