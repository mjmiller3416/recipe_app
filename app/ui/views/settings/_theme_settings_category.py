"""app/ui/views/settings/_theme_settings_category.py

Theme settings category widget for managing custom themes and appearance.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import shutil
from pathlib import Path
from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QPushButton,
                               QVBoxLayout, QWidget)

from _dev_tools import DebugLogger
from app.config import AppPaths
from app.style import Theme
from app.style.icon.config import Name, Type
from app.ui.components.layout.card import Card
from app.ui.components.widgets.button import Button
from ._base_category import BaseSettingsCategory


class ThemeSettingsCategory(BaseSettingsCategory):
    """Settings category for theme and appearance customization."""

    def __init__(self, parent=None):
        self._original_custom_theme_path = None
        self._original_use_custom_theme = False
        self._custom_theme_label = None
        self._import_button = None
        self._reset_theme_button = None
        super().__init__("theme", parent)

    def _build_ui(self) -> None:
        """Build the theme settings UI."""
        # Custom Theme Section
        theme_card = Card(card_type="Default")
        theme_card.setHeader("Custom Theme")
        theme_card.setSubHeader("Import and use your own custom theme files.")
        theme_card.expandWidth(True)

        # Theme import container
        theme_container = QWidget()
        theme_layout = QVBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(12)

        # Current theme status
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)

        theme_status_label = QLabel("Current Theme:")
        theme_status_label.setObjectName("SettingsLabel")

        self._custom_theme_label = QLabel("Default Theme")
        self._custom_theme_label.setObjectName("SettingsValue")

        status_layout.addWidget(theme_status_label)
        status_layout.addWidget(self._custom_theme_label)
        status_layout.addStretch()

        # Import button
        self._import_button = Button(
            label="Import Custom Theme",
            type=Type.PRIMARY,
            icon=Name.ADD
        )

        # Reset theme button
        self._reset_theme_button = Button(
            label="Reset to Default Theme",
            type=Type.SECONDARY,
            icon=Name.REFRESH
        )

        theme_layout.addLayout(status_layout)
        theme_layout.addWidget(self._import_button)
        theme_layout.addWidget(self._reset_theme_button)

        theme_card.addWidget(theme_container)
        self.layout.addWidget(theme_card)

        # Add stretch to push content to top
        self.layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        if self._import_button:
            self._import_button.clicked.connect(self._import_custom_theme)

        if self._reset_theme_button:
            self._reset_theme_button.clicked.connect(self._reset_to_default_theme)

    def _load_settings(self) -> None:
        """Load current settings into the UI."""
        self._original_custom_theme_path = self.settings_service.get("theme.custom_theme_path")
        self._original_use_custom_theme = self.settings_service.get("theme.use_custom_theme", False)

        self._update_theme_display()

    def _save_settings(self) -> None:
        """Save current UI values to settings."""
        # Settings are saved immediately when theme is imported or reset
        pass

    def get_changed_values(self) -> Dict[str, Any]:
        """Get dict of values that have changed from defaults."""
        changes = {}

        current_custom_path = self.settings_service.get("theme.custom_theme_path")
        current_use_custom = self.settings_service.get("theme.use_custom_theme", False)

        if current_custom_path != self._original_custom_theme_path:
            changes["custom_theme_path"] = current_custom_path

        if current_use_custom != self._original_use_custom_theme:
            changes["use_custom_theme"] = current_use_custom

        return changes

    def _update_theme_display(self) -> None:
        """Update the theme display label."""
        if not self._custom_theme_label:
            return

        use_custom = self.settings_service.get("theme.use_custom_theme", False)
        custom_path = self.settings_service.get("theme.custom_theme_path")

        if use_custom and custom_path:
            theme_name = Path(custom_path).stem
            self._custom_theme_label.setText(f"Custom: {theme_name}")
        else:
            self._custom_theme_label.setText("Default Theme")

    def _import_custom_theme(self) -> None:
        """Open file dialog to import a custom theme."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                source_path = Path(selected_files[0])
                self._process_theme_import(source_path)

    def _process_theme_import(self, source_path: Path) -> None:
        """Process the imported theme file."""
        try:
            # Ensure custom themes directory exists
            custom_themes_dir = AppPaths.CUSTOM_THEMES_DIR
            custom_themes_dir.mkdir(parents=True, exist_ok=True)

            # Copy theme file to custom themes directory
            destination_path = custom_themes_dir / source_path.name
            shutil.copy2(source_path, destination_path)

            # Update settings
            self.settings_service.set("theme.custom_theme_path", str(destination_path))
            self.settings_service.set("theme.use_custom_theme", True)

            # Apply the new theme
            from app.style.theme.config import Mode
            current_mode = Mode.LIGHT  # You might want to get this from current settings
            Theme.setCustomColorMap(str(destination_path), current_mode)

            # Update display
            self._update_theme_display()
            self._emit_settings_changed()

            DebugLogger.log(f"Custom theme imported: {source_path.name}", "info")

        except Exception as e:
            DebugLogger.log(f"Error importing custom theme: {e}", "error")

    def _reset_to_default_theme(self) -> None:
        """Reset to the default theme."""
        try:
            # Reset theme settings
            self.settings_service.set("theme.custom_theme_path", None)
            self.settings_service.set("theme.use_custom_theme", False)

            # Apply default theme
            from app.style.theme.config import Mode
            default_theme_path = AppPaths.MATERIAL_THEME_PATH
            current_mode = Mode.LIGHT  # You might want to get this from current settings
            Theme.setCustomColorMap(str(default_theme_path), current_mode)

            # Update display
            self._update_theme_display()
            self._emit_settings_changed()

            DebugLogger.log("Reset to default theme", "info")

        except Exception as e:
            DebugLogger.log(f"Error resetting to default theme: {e}", "error")