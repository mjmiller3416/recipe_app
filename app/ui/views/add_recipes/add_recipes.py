"""app/ui/views/add_recipes/add_recipes.py

This module defines the AddRecipes screen, which allows users to create new recipes
with ingredients, directions, and notes. It includes functionality for recipe image
management, dynamic ingredient forms, and comprehensive form validation.

The view follows the MVVM pattern with clear separation between UI presentation (View)
and business logic (ViewModel). Recipe creation is handled through coordinated ViewModels
for enhanced data validation and processing.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt

from _dev_tools import DebugLogger
from app.style import Qss, Theme
from app.style.icon.config import Name, Type
from app.ui.components.images import RecipeImage
from app.ui.components.layout.card import Card
from app.ui.components.widgets.button import Button
from app.ui.utils.form_utils import (
    clear_form_fields,
    collect_form_data,
    setup_tab_order_chain,
)
from app.ui.utils.layout_utils import (
    create_two_column_layout,
)
from app.ui.view_models.add_recipe_view_model import AddRecipeViewModel
from app.ui.view_models.ingredient_view_model import IngredientViewModel
from app.ui.views.base import ScrollableNavView
from ..add_recipes.cards import DirectionsNotesCard, IngredientsCard
from ..add_recipes.recipe_form import RecipeForm

class AddRecipes(ScrollableNavView):
    """Main add recipes view for creating new recipes with ingredients and directions.

    Allows users to create comprehensive recipes with:
    - Basic recipe information (name, category, time, servings)
    - Dynamic ingredient management with autocomplete
    - Directions and notes with toggleable interface
    - Recipe image upload and management

    Follows MVVM pattern with AddRecipeViewModel and IngredientViewModel handling business logic.
    """
    # ── Initialization ──────────────────────────────────────────────────────────────────────────────────────
    def __init__(self, parent=None):
        """Initialize the add recipes view.

        Args:
            parent: Optional parent widget.
        """
        # Initialize ViewModels BEFORE super() - required by _build_ui()
        self.add_recipe_view_model = AddRecipeViewModel()
        self.ingredient_view_model = IngredientViewModel()

        super().__init__(parent)
        DebugLogger.log("Initializing AddRecipes page", "info")
        self.setObjectName("AddRecipes")
        Theme.register_widget(self, Qss.ADD_RECIPE)

        # Track stored ingredients for form state management
        self.stored_ingredients = []

    def _connect_view_model_signals(self) -> None:
        """Connect ViewModel signals to UI update methods.

        Establishes communication between ViewModels and View for
        data updates, errors, validation, and state changes.
        """
        # AddRecipeViewModel signals
        self.add_recipe_view_model.recipe_saved_successfully.connect(self._on_recipe_saved_successfully)
        self.add_recipe_view_model.recipe_save_failed.connect(self._on_recipe_save_failed)
        self.add_recipe_view_model.validation_failed.connect(self._on_validation_failed)
        self.add_recipe_view_model.form_cleared.connect(self._on_form_cleared)

        # Enhanced data binding signals
        self.add_recipe_view_model.processing_state_changed.connect(self._on_processing_state_changed)
        self.add_recipe_view_model.form_validation_state_changed.connect(self._on_form_validation_state_changed)
        self.add_recipe_view_model.field_validation_error.connect(self._on_field_validation_error)
        self.add_recipe_view_model.field_validation_cleared.connect(self._on_field_validation_cleared)
        self.add_recipe_view_model.recipe_name_validated.connect(self._on_recipe_name_validated)
        self.add_recipe_view_model.loading_state_changed.connect(self._on_loading_state_changed)

        # IngredientViewModel signals
        self.ingredient_view_model.ingredient_name_validation_changed.connect(self._on_ingredient_name_validation_changed)
        self.ingredient_view_model.ingredient_category_validation_changed.connect(self._on_ingredient_category_validation_changed)
        self.ingredient_view_model.ingredient_quantity_validation_changed.connect(self._on_ingredient_quantity_validation_changed)

    # ── UI Setup ────────────────────────────────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        """Setup the UI components for the AddRecipes view.

        Creates comprehensive recipe creation form with sections for:
        recipe details, ingredients, directions/notes, and image upload.
        """
        self._create_recipe_details()
        self._create_ingredient_container()
        self._create_directions_notes_card()
        self._create_recipe_image()
        self._create_save_button()
        self._setup_layout()
        self._setup_tab_order()

    def _create_recipe_details(self):
        """Create the recipe details card with form fields."""
        self.recipe_details_card = Card(card_type="Default")
        self.recipe_details_card.setHeader("Recipe Info")
        self.recipe_details_card.setSubHeader("Basic information about your recipe.")
        self.recipe_details_card.expandWidth(True)
        self.recipe_form = RecipeForm()
        self.recipe_details_card.addWidget(self.recipe_form)

        # Expose form fields for direct access
        self.le_recipe_name = self.recipe_form.le_recipe_name
        self.cb_recipe_category = self.recipe_form.cb_recipe_category
        self.le_time = self.recipe_form.le_time
        self.cb_meal_type = self.recipe_form.cb_meal_type
        self.cb_dietary_preference = self.recipe_form.cb_dietary_preference
        self.le_servings = self.recipe_form.le_servings

    def _create_ingredient_container(self):
        """Create the ingredient container card."""
        self.ingredient_container = IngredientsCard(ingredient_view_model=self.ingredient_view_model)
        self.ingredient_container.expandWidth(True)

    def _create_directions_notes_card(self):
        """Create the directions and notes card."""
        self.directions_notes_card = DirectionsNotesCard()
        self.directions_notes_card.expandBoth(True)

        self.te_directions = self.directions_notes_card.te_directions
        self.te_notes = self.directions_notes_card.te_notes

    def _create_recipe_image(self):
        """Create the recipe image component."""
        self.recipe_image = RecipeImage()

    def _create_save_button(self):
        """Create the save button."""
        self.btn_save = Button("Save Recipe", Type.PRIMARY, Name.SAVE)
        self.btn_save.setObjectName("SaveRecipeButton")
        self.btn_save.clicked.connect(self._save_recipe)

    def _setup_layout(self):
        """Arrange all components in the scrollable layout."""
        self.content_layout.addWidget(self.recipe_details_card)
        self.content_layout.addWidget(self.ingredient_container)

        # Create directions/notes and image side by side
        column_layout = create_two_column_layout(
            left_widgets=[self.directions_notes_card],
            right_widgets=[self.recipe_image],
            left_weight=2,
            right_weight=1,
            match_heights=True
        )
        self.content_layout.addLayout(column_layout)

        # Add save button with spacing
        self.content_layout.addSpacing(20)
        self.content_layout.addWidget(self.btn_save, 0, Qt.AlignCenter)

    # ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────
    def _save_recipe(self):
        """Handle recipe save button click.

        Collects form data and delegates recipe creation to AddRecipeViewModel.
        Implements proper MVVM pattern by delegating all business logic to ViewModel.
        """
        DebugLogger.log("Starting recipe save process via ViewModel", "debug")

        # Collect raw form data
        raw_form_data = self._collect_form_data()

        # Transform to structured form data using ViewModel
        form_data = self.add_recipe_view_model.preprocess_form_data(raw_form_data)

        # Delegate recipe creation to ViewModel
        self.add_recipe_view_model.create_recipe(form_data)

    def _connect_signals(self):
        """Connect UI signals to their handlers for real-time validation."""
        # Connect form change handlers for real-time validation
        self.le_recipe_name.textChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("recipe_name", text))
        self.le_servings.textChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("servings", text))
        self.le_time.textChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("total_time", text))
        # TODO: Fix validation styling conflicts - validation applies inline styles that override QSS theme styling
        # self.cb_meal_type.currentTextChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("meal_type", text))

        # Connect recipe name and category for uniqueness checking
        self.le_recipe_name.editingFinished.connect(self._check_recipe_name_uniqueness)
        self.cb_recipe_category.currentTextChanged.connect(self._check_recipe_name_uniqueness)

    def _check_recipe_name_uniqueness(self):
        """Check recipe name uniqueness when name or category changes."""
        recipe_name = self.le_recipe_name.text().strip()
        category = self.cb_recipe_category.currentText().strip()

        if recipe_name and category:
            self.add_recipe_view_model.validate_recipe_name(recipe_name, category)

    # ── Public Interface ────────────────────────────────────────────────────────────────────────────────────
    def showEvent(self, event):
        """When the AddRecipes view is shown, focus the recipe name field."""
        super().showEvent(event)
        # Defer to ensure widget is active
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.le_recipe_name.setFocus)

    # ── Private Helper Methods ──────────────────────────────────────────────────────────────────────────────
    def _collect_form_data(self) -> dict:
        """Collect all form data from UI components for ViewModel processing."""
        # Collect recipe form data
        form_mapping = {
            "recipe_name": self.le_recipe_name,
            "recipe_category": self.cb_recipe_category,
            "meal_type": self.cb_meal_type,
            "dietary_preference": self.cb_dietary_preference,
            "total_time": self.le_time,
            "servings": self.le_servings,
            "directions": self.te_directions
        }
        recipe_data = collect_form_data(form_mapping)

        # Add notes from notes text edit
        recipe_data["notes"] = self.te_notes.toPlainText()

        # Add image paths
        recipe_data["reference_image_path"] = self.recipe_image.get_reference_image_path() or ""
        recipe_data["banner_image_path"] = ""  # Not currently used in UI

        # Collect ingredient data
        recipe_data["ingredients"] = self.ingredient_container.get_all_ingredients_data()

        return recipe_data

    def _clear_form(self):
        """Clear all form fields after successful save."""
        form_widgets = [
            self.le_recipe_name, self.cb_recipe_category, self.cb_meal_type,
            self.cb_dietary_preference, self.le_time, self.le_servings, self.te_directions
        ]
        clear_form_fields(form_widgets)
        self.recipe_image.clear_default_image()

        # Clear stored ingredients and widgets
        self.stored_ingredients.clear()
        self.ingredient_container.clear_all_ingredients()

    def _setup_tab_order(self):
        """Define a fixed tab order for keyboard navigation."""
        base_widgets = [
            self.le_recipe_name, self.le_time, self.le_servings,
            self.cb_meal_type, self.cb_recipe_category, self.cb_dietary_preference
        ]

        # Add ingredient widgets dynamically if they exist
        ingredient_widgets = self.ingredient_container.ingredient_widgets
        if ingredient_widgets:
            w = ingredient_widgets[0]
            ingredient_chain = [w.le_quantity, w.cb_unit, w.sle_ingredient_name,
                              w.cb_ingredient_category, w.btn_delete]
            base_widgets.extend(ingredient_chain)

        # Add final widgets
        base_widgets.append(self.te_directions)

        setup_tab_order_chain(base_widgets)

    def _to_payload(self):
        """Legacy method - now replaced by _collect_form_data and ViewModel processing."""
        DebugLogger.log("_to_payload called - consider using ViewModel pattern instead", "warning")
        return self._collect_form_data()

    # ── ViewModel Signal Handlers ───────────────────────────────────────────────────────────────────────────
    def _on_recipe_saved_successfully(self, recipe_name: str):
        """Handle successful recipe save from ViewModel."""
        message = f"Recipe '{recipe_name}' saved successfully!"
        self._display_save_message(message, success=True)

        # Clear form and reset state
        self._clear_form()
        self.stored_ingredients.clear()
        self.ingredient_container.clear_all_ingredients()

        DebugLogger.log(f"Recipe '{recipe_name}' saved successfully and form cleared", "info")

    def _on_recipe_save_failed(self, error_message: str):
        """Handle recipe save failure from ViewModel."""
        self._display_save_message(error_message, success=False)
        DebugLogger.log(f"Recipe save failed: {error_message}", "error")

    def _on_validation_failed(self, error_messages: list[str]):
        """Handle validation failure from ViewModel."""
        error_msg = "Please fix the following errors:\n• " + "\n• ".join(error_messages)
        self._display_save_message(error_msg, success=False)
        DebugLogger.log(f"Recipe validation failed: {error_messages}", "warning")

    def _on_form_cleared(self):
        """Handle form cleared signal from ViewModel."""
        self._clear_form()
        DebugLogger.log("Form cleared via ViewModel signal", "debug")

    def _on_processing_state_changed(self, is_processing: bool):
        """Handle processing state changes from ViewModel."""
        self.btn_save.setEnabled(not is_processing)
        if is_processing:
            self.btn_save.setText("Saving...")
        else:
            self.btn_save.setText("Save Recipe")

        DebugLogger.log(f"Processing state changed: {is_processing}", "debug")

    def _on_form_validation_state_changed(self, is_valid: bool):
        """Handle overall form validation state changes."""
        # Could be used to enable/disable save button based on validation
        # Currently handled by processing state, but available for future enhancements
        DebugLogger.log(f"Form validation state changed: {is_valid}", "debug")

    def _on_field_validation_error(self, field_name: str, error_message: str):
        """Handle field-specific validation errors."""
        self._apply_field_error_style(field_name, error_message)
        DebugLogger.log(f"Field validation error for {field_name}: {error_message}", "debug")

    def _on_field_validation_cleared(self, field_name: str):
        """Handle clearing of field validation errors."""
        self._clear_field_error_style(field_name)
        DebugLogger.log(f"Field validation cleared for {field_name}", "debug")

    def _on_recipe_name_validated(self, is_unique: bool, message: str):
        """Handle recipe name uniqueness validation results."""
        if not is_unique:
            self._apply_field_error_style("recipe_name", message)
        else:
            self._clear_field_error_style("recipe_name")
        DebugLogger.log(f"Recipe name validation: unique={is_unique}, message={message}", "debug")

    def _on_loading_state_changed(self, is_loading: bool, operation_description: str):
        """Handle loading state changes with operation descriptions."""
        if is_loading and operation_description:
            # Could show a progress indicator or status message
            DebugLogger.log(f"Loading: {operation_description}", "debug")
        elif not is_loading:
            DebugLogger.log("Loading completed", "debug")

    def _on_ingredient_name_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient name validation changes - delegated to ingredient forms."""
        # This will be connected to specific ingredient forms when they're created
        pass

    def _on_ingredient_category_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient category validation changes - delegated to ingredient forms."""
        # This will be connected to specific ingredient forms when they're created
        pass

    def _on_ingredient_quantity_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient quantity validation changes - delegated to ingredient forms."""
        # This will be connected to specific ingredient forms when they're created
        pass

    # ── User Feedback Methods ───────────────────────────────────────────────────────────────────────────────
    def _display_save_message(self, message: str, success: bool = True):
        """Display a toast notification for save operations.

        Args:
            message: The message to display.
            success: Whether this is a success or error message.
        """
        from app.ui.components.widgets import show_toast
        show_toast(self, message, success=success, duration=3000, offset_right=50)

    def _apply_field_error_style(self, field_name: str, error_message: str):
        """Apply error styling to a specific field and show tooltip.

        Args:
            field_name: The name of the field to apply error styling to.
            error_message: The error message to show in tooltip.
        """
        field_widget = self._get_field_widget(field_name)
        if field_widget:
            field_widget.setStyleSheet("border: 2px solid #f44336;")  # Material Design error red
            field_widget.setToolTip(error_message)

    def _clear_field_error_style(self, field_name: str):
        """Clear error styling from a specific field.

        Args:
            field_name: The name of the field to clear error styling from.
        """
        field_widget = self._get_field_widget(field_name)
        if field_widget:
            field_widget.setStyleSheet("")  # Reset to default styling
            field_widget.setToolTip("")

    def _get_field_widget(self, field_name: str):
        """Get the widget reference for a given field name.

        Args:
            field_name: The name of the field to get widget for.

        Returns:
            The widget associated with the field name, or None if not found.
        """
        field_mapping = {
            "recipe_name": self.le_recipe_name,
            "servings": self.le_servings,
            "total_time": self.le_time,
            "meal_type": self.cb_meal_type,
            "recipe_category": self.cb_recipe_category,
            "dietary_preference": self.cb_dietary_preference
        }
        return field_mapping.get(field_name)
