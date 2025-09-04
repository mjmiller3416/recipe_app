"""app/ui/views/settings.py

Settings view with category-based configuration interface.
Supports AI Image Generation settings and extensible for future categories.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from _dev_tools import DebugLogger
from app.core.services.ai_gen import ImageGenConfig, RecipeImageHelper
from app.core.services.settings_service import SettingsService
from app.style import Qss, Theme
from app.style.icon import Icon
from app.ui.components.layout.card import Card
from app.ui.components.widgets import Button, ComboBox
from app.ui.managers.navigation.views import MainView

# ── Settings Category ────────────────────────────────────────────────────────────────────────
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


# ── AI Image Generation Settings ─────────────────────────────────────────────────────────────
class ImageGenerationSettings(SettingsCategory):
    """AI Image Generation settings category."""

    def __init__(self, parent=None):
        super().__init__("ImageGeneration", parent)

        # Current config for reference
        self.config = ImageGenConfig()
        # Get recipe helper for prompt template
        from app.core.services.ai_gen.service import ImageGenService
        try:
            service = ImageGenService(self.config)
            self.recipe_helper = RecipeImageHelper(service, self.config)
            self.prompt_template = self.recipe_helper._BASE_PROMPT
        except RuntimeError:
            # Handle missing API key gracefully
            self.recipe_helper = None
            self.prompt_template = (
                "High-quality studio food photography of {recipe_name}. "
                "Style: natural light, shallow depth-of-field, appetizing, "
                "no text, no branding, no people. Plating on neutral surface. "
                "Composition clean and professional. White balance slightly warm. "
                "Ultra-detailed, realistic, crisp."
            )

        self.setHeader("AI Image Generation", Icon.SPARKLES)
        self.headerIcon.setSize(24, 24)
        self.headerIcon.setColor("primary")
        self.setContentMargins(25, 25, 25, 25)
        self.setSpacing(20)

        self._build_ui()

    def _build_ui(self):
        """Build the image generation settings UI."""

        # Model selection - horizontal layout (label + combobox)
        model_layout = QHBoxLayout()
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(15)

        model_label = QLabel("AI Model:")
        model_label.setObjectName("SettingsLabel")
        model_label.setMinimumWidth(120)

        # Available models with cost indicators
        model_options = [
            "gpt-image-1 (Latest - Higher Cost)",
            "dall-e-3 (Good Quality - Lower Cost)",
            "dall-e-2 (Basic Quality - Lowest Cost)"
        ]

        self.model_combobox = ComboBox(
            list_items=model_options,
            placeholder="Select AI model..."
        )
        self.model_combobox.setMinimumSize(440, 35)

        # Set current model
        current_model = self.config.model
        if current_model == "gpt-image-1":
            self.model_combobox.setCurrentIndex(0)
        elif current_model == "dall-e-3":
            self.model_combobox.setCurrentIndex(1)
        elif current_model == "dall-e-2":
            self.model_combobox.setCurrentIndex(2)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combobox, 1, Qt.AlignRight)

        self._content_layout.addLayout(model_layout)

        # Prompt template editing - horizontal layout (label + textedit)
        prompt_layout = QHBoxLayout()
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_layout.setSpacing(40)

        prompt_label = QLabel("Prompt Template:")
        prompt_label.setObjectName("SettingsLabel")
        prompt_label.setMinimumWidth(120)
        prompt_label.setAlignment(Qt.AlignTop)

        # Right side container for textedit and button
        prompt_container = QWidget()
        prompt_container_layout = QVBoxLayout(prompt_container)
        prompt_container_layout.setContentsMargins(0, 0, 0, 0)
        prompt_container_layout.setSpacing(20)

        # Warning message
        warning_label = QLabel("⚠️ Warning: Modifying the prompt may produce unexpected results. The default prompt is optimized for food photography.")
        warning_label.setObjectName("WarningText")
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: #ff9800; font-size: 16px; padding: 8px; background-color: rgba(255, 152, 0, 0.1); border-radius: 4px;")
        warning_label.setMaximumHeight(80)
        self.prompt_textedit = QTextEdit()
        self.prompt_textedit.setObjectName("SettingsTextEdit")
        self.prompt_textedit.setPlainText(self.prompt_template)
        self.prompt_textedit.setMaximumHeight(120)

        # Reset button for prompt
        self.reset_prompt_btn = Button("Reset to Default", "SECONDARY")
        self.reset_prompt_btn.clicked.connect(self._reset_prompt)

        prompt_container_layout.addWidget(warning_label)
        prompt_container_layout.addWidget(self.prompt_textedit)
        prompt_container_layout.addWidget(self.reset_prompt_btn)

        prompt_layout.addWidget(prompt_label)
        prompt_layout.addWidget(prompt_container)

        self._content_layout.addLayout(prompt_layout)

        # Connect signals
        self.model_combobox.currentTextChanged.connect(self._on_settings_changed)
        self.prompt_textedit.textChanged.connect(self._on_settings_changed)

    def _reset_prompt(self):
        """Reset prompt to default template."""
        default_prompt = (
            "High-quality studio food photography of {recipe_name}. "
            "Style: natural light, shallow depth-of-field, appetizing, "
            "no text, no branding, no people. Plating on neutral surface. "
            "Composition clean and professional. White balance slightly warm. "
            "Ultra-detailed, realistic, crisp."
        )
        self.prompt_textedit.setPlainText(default_prompt)

    def _on_settings_changed(self):
        """Emit signal when settings change."""
        settings = self.get_settings()
        self.settings_changed.emit(self.category_name, settings)

    def get_settings(self) -> Dict[str, Any]:
        """Get current image generation settings."""
        # Extract model name from combobox text
        model_text = self.model_combobox.currentText()
        if "gpt-image-1" in model_text:
            model = "gpt-image-1"
        elif "dall-e-3" in model_text:
            model = "dall-e-3"
        elif "dall-e-2" in model_text:
            model = "dall-e-2"
        else:
            model = "gpt-image-1"  # default

        return {
            "model": model,
            "prompt_template": self.prompt_textedit.toPlainText().strip()
        }

    def set_settings(self, settings: Dict[str, Any]):
        """Apply image generation settings."""
        if "model" in settings:
            model = settings["model"]
            if model == "gpt-image-1":
                self.model_combobox.setCurrentIndex(0)
            elif model == "dall-e-3":
                self.model_combobox.setCurrentIndex(1)
            elif model == "dall-e-2":
                self.model_combobox.setCurrentIndex(2)

        if "prompt_template" in settings:
            self.prompt_textedit.setPlainText(settings["prompt_template"])

    def validate_settings(self) -> bool:
        """Validate image generation settings."""
        # Check if model is selected
        if not self.model_combobox.currentText():
            return False

        # Check if prompt is not empty
        if not self.prompt_textedit.toPlainText().strip():
            return False

        return True


# ── Settings ─────────────────────────────────────────────────────────────────────────────────
class Settings(MainView):
    """Main Settings view with category selection and management."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Settings")

        # Register for theme management
        Theme.register_widget(self, Qss.SETTINGS)

        # Settings data
        self.settings_service = SettingsService()
        self.categories: Dict[str, SettingsCategory] = {}

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        """Build the main settings interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Left sidebar for categories
        self._build_category_sidebar(main_layout)

        # Right content area
        self._build_content_area(main_layout)

        # Add categories
        self._add_categories()

    def _build_category_sidebar(self, main_layout: QHBoxLayout):
        """Build the category selection sidebar."""
        sidebar_container = Card()
        sidebar_container.setObjectName("CategorySidebar")
        sidebar_container.setHeader("Categories", Icon.SETTINGS)
        sidebar_container.headerIcon.setSize(20, 20)
        sidebar_container.setContentMargins(20, 20, 20, 20)
        sidebar_container.setSpacing(10)
        sidebar_container.setMinimumWidth(320)
        sidebar_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Category buttons will be added here
        self.category_buttons_layout = QVBoxLayout()
        self.category_buttons_layout.setSpacing(5)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(self.category_buttons_layout)
        sidebar_container.addWidget(sidebar_widget)

        # Add stretch to push buttons to top
        self.category_buttons_layout.addStretch()

        main_layout.addWidget(sidebar_container, 0)

    def _build_content_area(self, main_layout: QHBoxLayout):
        """Build the settings content area."""
        # Content area with scroll
        content_container = QWidget()
        content_container.setObjectName("SettingsContent")

        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Scroll area for settings
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Settings content widget
        self.settings_content = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_content)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(25)
        self.settings_layout.addStretch()

        self.scroll_area.setWidget(self.settings_content)
        content_layout.addWidget(self.scroll_area)

        # Action buttons at bottom
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(20, 20, 20, 20)
        actions_layout.setSpacing(15)

        self.save_btn = Button("Save Settings", "PRIMARY")
        self.reset_btn = Button("Reset to Defaults", "SECONDARY")

        actions_layout.addStretch()
        actions_layout.addWidget(self.reset_btn)
        actions_layout.addWidget(self.save_btn)

        content_layout.addWidget(actions_container)

        # Connect action buttons
        self.save_btn.clicked.connect(self._save_settings)
        self.reset_btn.clicked.connect(self._reset_to_defaults)

        main_layout.addWidget(content_container, 1)

    def _add_categories(self):
        """Add all settings categories."""
        # AI Image Generation category
        img_gen_category = ImageGenerationSettings()
        img_gen_category.settings_changed.connect(self._on_category_changed)
        self._add_category("AI Image Generation", img_gen_category)

        # Select first category by default
        if self.categories:
            first_category = next(iter(self.categories.keys()))
            self._show_category(first_category)

    def _add_category(self, name: str, category: SettingsCategory):
        """Add a settings category."""
        self.categories[name] = category

        # Add category button
        category_btn = Button(name, "SECONDARY")
        category_btn.setObjectName("CategoryButton")
        category_btn.setCheckable(True)
        category_btn.clicked.connect(lambda: self._show_category(name))

        # Insert before stretch
        self.category_buttons_layout.insertWidget(
            self.category_buttons_layout.count() - 1,
            category_btn
        )

        # Store button reference
        category.category_button = category_btn

    def _show_category(self, category_name: str):
        """Show the selected category settings."""
        # Clear current content
        for i in reversed(range(self.settings_layout.count() - 1)):  # Keep stretch at end
            item = self.settings_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Update button states
        for name, category in self.categories.items():
            if hasattr(category, 'category_button'):
                category.category_button.setChecked(name == category_name)

        # Show selected category
        if category_name in self.categories:
            category = self.categories[category_name]
            self.settings_layout.insertWidget(0, category)

    def _on_category_changed(self, category_name: str, settings: Dict[str, Any]):
        """Handle settings change in a category."""
        DebugLogger().log(f"Settings changed in {category_name}: {settings}", "debug")

    def _load_settings(self):
        """Load settings from settings service."""
        try:
            # Load image generation settings
            img_gen_settings = self.settings_service.get_image_generation_settings()
            img_gen_category = self.categories.get("AI Image Generation")
            if img_gen_category:
                img_gen_category.set_settings(img_gen_settings)

            DebugLogger().log("Settings loaded successfully", "info")
        except Exception as e:
            DebugLogger().log(f"Error loading settings: {e}", "warning")

    def _save_settings(self):
        """Save all settings using settings service."""
        try:
            # Save each category
            for name, category in self.categories.items():
                if category.validate_settings():
                    if name == "AI Image Generation":
                        settings = category.get_settings()
                        success = self.settings_service.update_image_generation_settings(settings)
                        if not success:
                            raise Exception("Failed to save image generation settings")

            DebugLogger().log("Settings saved successfully", "info")

            # Reload AI service configuration for immediate effect
            self._reload_ai_services()

            # TODO: Show success toast notification

        except Exception as e:
            DebugLogger().log(f"Error saving settings: {e}", "error")
            # TODO: Show error toast notification

    def _reload_ai_services(self):
        """Reload AI image generation services to apply new settings."""
        try:
            # Try to find and reload AI services in other views
            # This is a workaround since we don't have a proper service registry

            # Get navigation service through main window if possible
            main_window = self.window()
            if hasattr(main_window, 'navigation'):
                navigation = main_window.navigation
                reloaded_count = 0

                # Reload AddRecipes AI service
                add_recipes = navigation.page_instances.get("add_recipe")
                if add_recipes and hasattr(add_recipes, 'reload_ai_service'):
                    if add_recipes.reload_ai_service():
                        reloaded_count += 1

                # Note: FullRecipe is created dynamically, so we can't reload it here

                if reloaded_count > 0:
                    DebugLogger().log(f"Reloaded {reloaded_count} AI service(s) with new settings", "info")
                else:
                    DebugLogger().log("AI service settings updated - changes will apply to new generations", "info")
            else:
                DebugLogger().log("AI service settings updated - changes will apply to new instances", "info")

        except Exception as e:
            DebugLogger().log(f"Error reloading AI services: {e}", "warning")

    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        try:
            # Reset each category
            for category in self.categories.values():
                if isinstance(category, ImageGenerationSettings):
                    default_config = ImageGenConfig()
                    default_prompt = (
                        "High-quality studio food photography of {recipe_name}. "
                        "Style: natural light, shallow depth-of-field, appetizing, "
                        "no text, no branding, no people. Plating on neutral surface. "
                        "Composition clean and professional. White balance slightly warm. "
                        "Ultra-detailed, realistic, crisp."
                    )
                    default_settings = {
                        "model": default_config.model,
                        "prompt_template": default_prompt
                    }
                    category.set_settings(default_settings)

            DebugLogger().log("Settings reset to defaults", "info")
            # TODO: Show reset confirmation toast

        except Exception as e:
            DebugLogger().log(f"Error resetting settings: {e}", "error")
