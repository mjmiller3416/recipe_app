"""app/ui/views/settings.py

Settings View with category-based configuration interface.
Supports multiple settings categories with navigation and save/reset functionality.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QWidget)

from _dev_tools import DebugLogger
from app.core.services.settings_service import SettingsService
from app.style.icon.config import Name, Type
from app.ui.components.widgets.button import Button
from app.ui.views.base import BaseView
from ._user_settings_category import UserSettingsCategory
from ._theme_settings_category import ThemeSettingsCategory


class Settings(BaseView):
    """Main Settings view with category selection and management."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Settings")

        # Settings data
        self.settings_service = SettingsService()
        self.categories = {}
        self.has_unsaved_changes = False

        self._build_ui()
        self._setup_categories()
        self._connect_signals()

    def _build_ui(self):
        """Build the main settings interface."""
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Tab navigation + content
        self.tab_widget = self._create_tab_widget()
        main_layout.addWidget(self.tab_widget)

        # Bottom action buttons
        buttons_widget = self._create_action_buttons()
        main_layout.addWidget(buttons_widget)

        # Set the main layout
        container = QWidget()
        container.setObjectName("SettingsContainer")
        container.setLayout(main_layout)
        self.content_layout.addWidget(container)

    def _create_tab_widget(self) -> QTabWidget:
        """Create the tab widget for settings categories."""
        tab_widget = QTabWidget()
        tab_widget.setObjectName("SettingsTabWidget")
        tab_widget.setTabPosition(QTabWidget.North)
        tab_widget.setDocumentMode(True)
        tab_widget.setElideMode(Qt.ElideNone)
        # remove the default base line above the tabs
        tab_widget.tabBar().setDrawBase(False)
        return tab_widget

    def _create_action_buttons(self) -> QWidget:
        """Create the bottom action buttons area."""
        buttons_widget = QWidget()
        buttons_widget.setObjectName("SettingsActionButtons")

        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 16, 0, 0)
        buttons_layout.setSpacing(12)

        # Add stretch to push buttons to the right
        buttons_layout.addStretch()

        # Reset button
        self.reset_button = Button(
            label="Reset All",
            type=Type.SECONDARY,
            icon=Name.REFRESH
        )
        self.reset_button.setObjectName("SettingsResetButton")

        # Save button
        self.save_button = Button(
            label="Save Changes",
            type=Type.PRIMARY,
            icon=Name.SAVE
        )
        self.save_button.setObjectName("SettingsSaveButton")
        self.save_button.setEnabled(False)

        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.save_button)

        return buttons_widget

    def _setup_categories(self) -> None:
        """Setup and add all settings categories."""
        # User Settings Category
        user_category = UserSettingsCategory()
        self.categories["user"] = user_category
        self.tab_widget.addTab(user_category, "User Settings")

        # Theme Settings Category
        theme_category = ThemeSettingsCategory()
        self.categories["theme"] = theme_category
        self.tab_widget.addTab(theme_category, "Theme")
        self.tab_widget.setCurrentIndex(0)

    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        # Navigation
        self.tab_widget.currentChanged.connect(self._on_category_changed)

        # Action buttons
        self.save_button.clicked.connect(self._save_all_settings)
        self.reset_button.clicked.connect(self._reset_all_settings)

        # Category change signals
        for category in self.categories.values():
            category.settings_changed.connect(self._on_settings_changed)

    def _on_category_changed(self, index: int = 0) -> None:
        """Handle navigation category change."""
        try:
            key = list(self.categories.keys())[index]
            DebugLogger.log(f"Switched to {key} settings", "debug")
        except Exception:
            pass

    def _on_settings_changed(self, category_name: str, changed_values: dict) -> None:
        """Handle when settings in any category change."""
        self.has_unsaved_changes = bool(changed_values)
        self.save_button.setEnabled(self.has_unsaved_changes)
        DebugLogger.log(f"Settings changed in {category_name}: {changed_values}", "debug")

    def _save_all_settings(self) -> None:
        """Save all settings across all categories."""
        try:
            success_count = 0
            for category_name, category_widget in self.categories.items():
                if category_widget.save_category():
                    success_count += 1
                    DebugLogger.log(f"Saved {category_name} settings", "info")
                else:
                    DebugLogger.log(f"Failed to save {category_name} settings", "error")

            if success_count == len(self.categories):
                self.has_unsaved_changes = False
                self.save_button.setEnabled(False)
                DebugLogger.log("All settings saved successfully", "info")

                # Show success message
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "All settings have been saved successfully."
                )
            else:
                DebugLogger.log("Some settings failed to save", "warning")
                QMessageBox.warning(
                    self,
                    "Save Warning",
                    "Some settings may not have been saved properly. Please check the logs and try again."
                )

        except Exception as e:
            DebugLogger.log(f"Error saving settings: {e}", "error")

    def _reset_all_settings(self) -> None:
        """Reset all settings to defaults with confirmation."""
        reply = QMessageBox.question(
            self,
            "Reset All Settings",
            "Are you sure you want to reset all settings to their default values?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Reset all categories
                if self.settings_service.reset_to_defaults():
                    # Reload all category widgets
                    for category_widget in self.categories.values():
                        category_widget._load_settings()

                    self.has_unsaved_changes = False
                    self.save_button.setEnabled(False)
                    DebugLogger.log("All settings reset to defaults", "info")

                    # Show success message
                    QMessageBox.information(
                        self,
                        "Settings Reset",
                        "All settings have been successfully reset to their default values."
                    )
                else:
                    DebugLogger.log("Failed to reset settings", "error")
                    QMessageBox.critical(
                        self,
                        "Reset Failed",
                        "Failed to reset settings. Please try again."
                    )

            except Exception as e:
                DebugLogger.log(f"Error resetting settings: {e}", "error")
                QMessageBox.critical(
                    self,
                    "Reset Failed",
                    f"An error occurred while resetting settings:\n{str(e)}"
                )
