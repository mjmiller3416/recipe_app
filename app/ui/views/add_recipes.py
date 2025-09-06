"""app/ui/pages/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QTextEdit, QWidget

from _dev_tools import DebugLogger
from app.config import (
    DIETARY_PREFERENCES,
    FLOAT_VALIDATOR,
    INGREDIENT_CATEGORIES,
    MEAL_TYPE,
    MEASUREMENT_UNITS,
    NAME_PATTERN,
    RECIPE_CATEGORIES,
)
from app.style import Qss, Theme
from app.style.icon.config import Name, Type
from app.ui.components.images import RecipeImage
from app.ui.components.inputs import SmartLineEdit
from app.ui.components.layout.card import ActionCard, Card
from app.ui.components.widgets import ComboBox, ToolButton
from app.ui.components.widgets.button import Button
from app.ui.utils.form_utils import (
    clear_error_styles,
    clear_form_fields,
    collect_form_data,
    dynamic_validation,
    setup_tab_order_chain,
)
from app.ui.utils.layout_utils import (
    create_labeled_form_grid,
    create_two_column_layout,
)
from app.ui.view_models.add_recipe_view_model import AddRecipeViewModel
from app.ui.view_models.ingredient_view_model import IngredientViewModel
from app.ui.views.base import ScrollableNavView

# ── Forms ───────────────────────────────────────────────────────────────────────────────────────────────────
class RecipeForm(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RecipeForm")

        # ── Configure declarative form layout ──
        field_configs = {
            "recipe_name": {
                "widget_type": "line_edit",
                "label": "Recipe Name",
                "placeholder": "e.g. Spaghetti Carbonara",
                "object_name": "RecipeNameLineEdit",
                "row": 0, "col": 0, "col_span": 2
            },
            "time": {
                "widget_type": "line_edit",
                "label": "Total Time",
                "placeholder": "e.g. 30 mins",
                "object_name": "TotalTimeLineEdit",
                "row": 2, "col": 0
            },
            "servings": {
                "widget_type": "line_edit",
                "label": "Servings",
                "placeholder": "e.g. 4",
                "object_name": "ServingsLineEdit",
                "row": 2, "col": 1
            },
            "meal_type": {
                "widget_type": "combo_box",
                "label": "Meal Type",
                "placeholder": "Select meal type",
                "list_items": MEAL_TYPE,
                "object_name": "ComboBox",
                "context": "recipe_form",
                "row": 4, "col": 0
            },
            "recipe_category": {
                "widget_type": "combo_box",
                "label": "Category",
                "placeholder": "Select category",
                "list_items": RECIPE_CATEGORIES,
                "object_name": "ComboBox",
                "context": "recipe_form",
                "row": 4, "col": 1
            },
            "dietary_preference": {
                "widget_type": "combo_box",
                "label": "Dietary Preference",
                "placeholder": "Select dietary preference",
                "list_items": DIETARY_PREFERENCES,
                "object_name": "ComboBox",
                "context": "recipe_form",
                "row": 6, "col": 0
            }
        }

        self._layout, form_widgets, form_labels = create_labeled_form_grid(
            self, field_configs, fixed_height=60,
        )

        # Assign widgets to self attributes for compatibility
        self.le_recipe_name = form_widgets["recipe_name"]
        self.le_time = form_widgets["time"]
        self.le_servings = form_widgets["servings"]
        self.cb_meal_type = form_widgets["meal_type"]
        self.cb_recipe_category = form_widgets["recipe_category"]
        self.cb_dietary_preference = form_widgets["dietary_preference"]

        # Assign labels to self attributes
        self.lbl_recipe_name = form_labels["recipe_name"]
        self.lbl_time = form_labels["time"]
        self.lbl_servings = form_labels["servings"]
        self.lbl_meal_type = form_labels["meal_type"]
        self.lbl_category = form_labels["recipe_category"]
        self.lbl_dietary_preference = form_labels["dietary_preference"]

class IngredientForm(QWidget):
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)
    ingredient_data_changed = Signal()  # New signal for data changes

    def __init__(self, ingredient_view_model=None, removable=True, parent=None):
        """
        Initializes the IngredientForm with a grid layout and sets up UI components.
        The ingredient name input is an editable ComboBox populated with existing
        ingredient names. Selecting an existing ingredient auto-populates its category.

        Args:
            ingredient_view_model (IngredientViewModel): ViewModel for ingredient operations
            removable (bool): If True, the widget will have a remove button.
            parent (QWidget, optional): Parent widget for this ingredient widget.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Register with Theme API for Material3 styling
        Theme.register_widget(self, Qss.INGREDIENT_WIDGET)

        # Create horizontal layout for row-based design
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(18, 18, 18, 18)
        self.main_layout.setSpacing(12)
        self.setObjectName("IngredientForm")

        # Store ViewModel reference - no direct Core service access
        self.ingredient_view_model = ingredient_view_model
        self.exact_match = None
        self._build_ui()
        self.setup_event_logic()

    def _build_ui(self):
        """Sets up the UI components and layout for the ingredient widget."""

        # Drag handle for reordering
        self.drag_handle = ToolButton(Type.DEFAULT, Name.GRIP_DOTS)
        self.drag_handle.setObjectName("DragHandle")
        self.drag_handle.setIconSize(24, 24)
        self.drag_handle.setStateDefault("on_surface")
        self.drag_handle.setStateHover("tertiary")
        self.main_layout.addWidget(self.drag_handle)

        # Unit field - compact (create first to get reference height)
        self.cb_unit = ComboBox(
            list_items=MEASUREMENT_UNITS,
            placeholder="Unit"
        )
        self.cb_unit.setObjectName("ComboBox UnitField")
        self.main_layout.addWidget(self.cb_unit)

        # Get the ComboBox height to use for other fields
        combobox_height = self.cb_unit.sizeHint().height()

        # Quantity field - compact
        self.le_quantity = QLineEdit(self)
        self.le_quantity.setPlaceholderText("Qty")
        self.le_quantity.setObjectName("QuantityField")
        self.le_quantity.setFixedHeight(combobox_height)
        self.main_layout.addWidget(self.le_quantity)

        # Ingredient name field - expandable with lazy loading optimization
        # Performance optimization: start with empty list, populate on first focus
        self.sle_ingredient_name = SmartLineEdit(
            list_items=[],  # Start empty for faster initialization
            placeholder="Ingredient Name"
        )

        # Set up lazy loading for autocomplete data
        self._autocomplete_loaded = False
        self.sle_ingredient_name.setObjectName("NameField")
        self.sle_ingredient_name.setFixedHeight(combobox_height)
        self.main_layout.addWidget(self.sle_ingredient_name)

        # Category field - medium width
        self.cb_ingredient_category = ComboBox(
            list_items=INGREDIENT_CATEGORIES,
            placeholder="Category"
        )
        self.cb_ingredient_category.setObjectName("ComboBox CategoryField")
        self.main_layout.addWidget(self.cb_ingredient_category)

        # Delete button - replaces subtract/add buttons
        self.btn_delete = ToolButton(Type.DEFAULT, Name.TRASH)
        self.btn_delete.setObjectName("DeleteButton")
        self.btn_delete.setIconSize(32, 32)
        self.btn_delete.setStateDefault("on_surface")
        self.btn_delete.setStateHover("tertiary")
        self.main_layout.addWidget(self.btn_delete)

        # Set stretch factors for proper proportions
        self.main_layout.setStretchFactor(self.drag_handle, 0)
        self.main_layout.setStretchFactor(self.cb_unit, 0)  # Fixed width
        self.main_layout.setStretchFactor(self.le_quantity, 0)  # Fixed width
        self.main_layout.setStretchFactor(self.sle_ingredient_name, 3)  # Expandable
        self.main_layout.setStretchFactor(self.cb_ingredient_category, 0)  # Fixed width
        self.main_layout.setStretchFactor(self.btn_delete, 0)

    def setup_event_logic(self):
        """Connects signals to their respective slots for handling ingredient data."""
        self.btn_delete.clicked.connect(self.request_removal)
        # Note: Add ingredient functionality will be handled at container level

        dynamic_validation(self.le_quantity, FLOAT_VALIDATOR)

        # Performance optimization: lazy load autocomplete data on first focus
        self.sle_ingredient_name.focusInEvent = self._on_ingredient_name_focus_in

        # Connect real-time validation through ViewModel
        self.sle_ingredient_name.currentTextChanged.connect(self._ingredient_name_changed)
        if self.ingredient_view_model:
            self.sle_ingredient_name.textChanged.connect(
                lambda text: self.ingredient_view_model.validate_ingredient_name_real_time(text)
            )
            self.cb_ingredient_category.currentTextChanged.connect(
                lambda text: self.ingredient_view_model.validate_ingredient_category_real_time(text)
            )
            self.le_quantity.textChanged.connect(
                lambda text: self.ingredient_view_model.validate_ingredient_quantity_real_time(text)
            )

            # Connect ViewModel validation signals to UI updates
            self.ingredient_view_model.ingredient_name_validation_changed.connect(self._on_name_validation_changed)
            self.ingredient_view_model.ingredient_category_validation_changed.connect(self._on_category_validation_changed)
            self.ingredient_view_model.ingredient_quantity_validation_changed.connect(self._on_quantity_validation_changed)

    def _ingredient_name_changed(self, text: str):
        """
        Handles changes in the ingredient name field (SmartLineEdit).
        If the entered text matches an existing ingredient (case-insensitive exact match),
        its category is auto-populated and the category ComboBox may be disabled.
        Otherwise, the category ComboBox is enabled for manual input.
        """
        current_text = text.strip()
        self.cb_ingredient_category.setEnabled(True)

        if not current_text:
            self.cb_ingredient_category.setCurrentIndex(-1)
            clear_error_styles(self.sle_ingredient_name)
            self.exact_match = None
            self.ingredient_data_changed.emit()
            return

        # validate the ingredient name against the NAME_PATTERN
        if not NAME_PATTERN.match(current_text):
            self.sle_ingredient_name.setStyleSheet("border: 1px solid red;")
            self.exact_match = None
            self.ingredient_data_changed.emit()
            return
        else:
            clear_error_styles(self.sle_ingredient_name)

        # Use ViewModel for ingredient matching if available
        if self.ingredient_view_model:
            match_result = self.ingredient_view_model.find_ingredient_matches(current_text)

            if match_result.exact_match:
                self.exact_match = match_result.exact_match
                category = match_result.exact_match.ingredient_category

                # Find and set category in ComboBox
                category_index = self.cb_ingredient_category.findText(
                    category,
                    Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive,
                )

                if category_index < 0:
                    category_index = self.cb_ingredient_category.findText(
                        category,
                        Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchContains,
                    )

                if category_index >= 0:
                    self.cb_ingredient_category.setCurrentIndex(category_index)
                else:
                    self.cb_ingredient_category.addItem(category)
                    self.cb_ingredient_category.setCurrentText(category)

                clear_error_styles(self.cb_ingredient_category)
            else:
                self.exact_match = None
                # Suggest category if available
                if match_result.suggested_category:
                    category_index = self.cb_ingredient_category.findText(
                        match_result.suggested_category,
                        Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive,
                    )
                    if category_index >= 0:
                        self.cb_ingredient_category.setCurrentIndex(category_index)
                else:
                    self.cb_ingredient_category.setCurrentIndex(-1)

                self.cb_ingredient_category.setEnabled(True)
        else:
            # Fallback when no ViewModel is available
            self.exact_match = None
            self.cb_ingredient_category.setCurrentIndex(-1)
            self.cb_ingredient_category.setEnabled(True)

        # Emit signal to notify parent of data changes
        self.ingredient_data_changed.emit()

    def _on_ingredient_name_focus_in(self, event):
        """Handle focus in event for ingredient name field with lazy loading."""
        # Performance optimization: load autocomplete data only when needed
        if not self._autocomplete_loaded and self.ingredient_view_model:
            try:
                # Load autocomplete cache if not already loaded
                if not self.ingredient_view_model._cache_loaded:
                    self.ingredient_view_model._load_autocomplete_cache()

                # Update SmartLineEdit with autocomplete data
                ingredient_names = self.ingredient_view_model._autocomplete_cache
                if ingredient_names:
                    self.sle_ingredient_name.source.setStringList(ingredient_names)
                    self._autocomplete_loaded = True
                    DebugLogger.log(f"Loaded {len(ingredient_names)} ingredient names for autocomplete", "debug")

            except Exception as e:
                DebugLogger.log(f"Failed to lazy load ingredient names: {e}", "warning")

        # Call original focus in event
        from PySide6.QtWidgets import QLineEdit
        QLineEdit.focusInEvent(self.sle_ingredient_name, event)

    def get_ingredient_data(self) -> dict:
        """Returns the ingredient data as a dictionary for external collection."""
        return self._to_payload()

    def request_removal(self):
        """Emits a signal to request removal of this ingredient widget."""
        if self.parent() and len(self.parent().findChildren(IngredientForm)) > 1:
            self.remove_ingredient_requested.emit(self)

    def _to_payload(self) -> dict:
        """Returns a plain dict that matches RecipeIngredientDTO fields"""
        # Import here to avoid circular imports
        from app.core.utils.conversion_utils import safe_float_conversion
        from app.core.utils.text_utils import sanitize_form_input

        return {
            "ingredient_name": sanitize_form_input(self.sle_ingredient_name.text()),
            "ingredient_category": sanitize_form_input(self.cb_ingredient_category.currentText()),
            "unit": sanitize_form_input(self.cb_unit.currentText()),
            "quantity": safe_float_conversion(self.le_quantity.text().strip()),
            "existing_ingredient_id": self.exact_match.id if self.exact_match else None,
        }

    # ── Validation Event Handlers ───────────────────────────────────────────────────────────────────────────────

    def _on_name_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient name validation changes."""
        if is_valid:
            self.sle_ingredient_name.setStyleSheet("")
            self.sle_ingredient_name.setToolTip("")
        else:
            self.sle_ingredient_name.setStyleSheet("border: 2px solid #f44336;")
            self.sle_ingredient_name.setToolTip(error_message)

    def _on_category_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient category validation changes."""
        if is_valid:
            self.cb_ingredient_category.setStyleSheet("")
            self.cb_ingredient_category.setToolTip("")
        else:
            self.cb_ingredient_category.setStyleSheet("border: 2px solid #f44336;")
            self.cb_ingredient_category.setToolTip(error_message)

    def _on_quantity_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient quantity validation changes."""
        if is_valid:
            self.le_quantity.setStyleSheet("")
            self.le_quantity.setToolTip("" if not error_message else error_message)  # Keep warnings as tooltips
        else:
            self.le_quantity.setStyleSheet("border: 2px solid #f44336;")
            self.le_quantity.setToolTip(error_message)

    def cleanup(self):
        """Clean up resources to prevent memory leaks."""
        try:
            # Disconnect signals to prevent lingering connections
            if self.ingredient_view_model:
                self.ingredient_view_model.ingredient_name_validation_changed.disconnect()
                self.ingredient_view_model.ingredient_category_validation_changed.disconnect()
                self.ingredient_view_model.ingredient_quantity_validation_changed.disconnect()

            # Clear autocomplete data to free memory
            if hasattr(self, 'sle_ingredient_name') and self.sle_ingredient_name.source:
                self.sle_ingredient_name.source.setStringList([])

            # Clear references
            self.ingredient_view_model = None
            self.exact_match = None

            DebugLogger.log("IngredientForm cleaned up successfully", "debug")

        except Exception as e:
            DebugLogger.log(f"Error during IngredientForm cleanup: {e}", "warning")


# ── Containers ──────────────────────────────────────────────────────────────────────────────────────────────
class IngredientsCard(ActionCard):
    """
    Container for managing ingredient widgets within a Card.
    Provides add/remove functionality and data collection.
    """

    ingredients_changed = Signal()  # Emitted when ingredients are added/removed

    def __init__(self, ingredient_view_model=None, parent=None):
        """Initialize the ingredient container."""
        super().__init__(card_type="Default", parent=parent)

        self.setHeader("Ingredients")
        self.setSubHeader("List all the ingredients required for this recipe.")

        self.ingredient_view_model = ingredient_view_model
        self.ingredient_widgets = []
        self._build_ui()

    def _build_ui(self):
        """Set up the container UI with initial ingredient and add button."""

        # Add initial ingredient widget
        self._add_ingredient_widget()

        # Add button to card footer with left alignment and ADD icon
        self.addButton("Add Ingredient", icon=Name.ADD, alignment=Qt.AlignLeft)

        # Customize button icon size and connect click event
        if self.button:
            self.button.setIconSize(24, 24)  # Set custom icon size
            self.button.clicked.connect(self._add_ingredient_widget)

    def _add_ingredient_widget(self):
        """Add a new ingredient widget to the container."""
        ingredient_widget = IngredientForm(ingredient_view_model=self.ingredient_view_model)
        ingredient_widget.remove_ingredient_requested.connect(self._remove_ingredient_widget)

        self.ingredient_widgets.append(ingredient_widget)
        self.addWidget(ingredient_widget)

        self.ingredients_changed.emit()

    def _remove_ingredient_widget(self, widget: IngredientForm):
        """Remove an ingredient widget from the container with proper cleanup."""
        if len(self.ingredient_widgets) <= 1:
            return  # Always keep at least one ingredient widget

        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)
            self.removeWidget(widget)

            # Performance optimization: cleanup resources before deletion
            widget.cleanup()
            widget.deleteLater()

        self.ingredients_changed.emit()

    def get_all_ingredients_data(self) -> list[dict]:
        """Collect data from all ingredient widgets."""
        ingredients_data = []

        for widget in self.ingredient_widgets:
            data = widget.get_ingredient_data()
            # Only include ingredients with at least a name
            if data.get("ingredient_name", "").strip():
                ingredients_data.append(data)

        return ingredients_data

    def clear_all_ingredients(self):
        """Clear all ingredient widgets with proper cleanup and add one empty one."""
        # Performance optimization: cleanup resources before removal
        for widget in self.ingredient_widgets:
            self.removeWidget(widget)
            widget.cleanup()  # Clean up resources before deletion
            widget.deleteLater()

        self.ingredient_widgets.clear()

        # Add one fresh ingredient widget
        self._add_ingredient_widget()

    def get_ingredient_count(self) -> int:
        """Get the number of ingredient widgets."""
        return len(self.ingredient_widgets)

class DirectionsNotesCard(Card):
    """Custom card with toggle between Directions and Notes content."""

    def __init__(self, parent=None):
        super().__init__(card_type="Default")
        self.setHeader("Directions & Notes")
        self.setMinimumHeight(600)  # set minimum height to ensure enough space for content

        # Create toggle buttons container
        self.toggle_container = QWidget()
        self.toggle_container.setObjectName("ToggleContainer")
        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(1, 1, 1, 1)
        toggle_layout.setSpacing(0)

        # Create toggle buttons using custom Button class
        self.btn_directions = Button("Directions", Type.PRIMARY)
        self.btn_notes = Button("Notes", Type.SECONDARY)

        # Set object names for styling
        self.btn_directions.setObjectName("ToggleButtonActive")
        self.btn_notes.setObjectName("ToggleButtonInactive")

        # Add buttons to toggle layout
        toggle_layout.addWidget(self.btn_directions)
        toggle_layout.addWidget(self.btn_notes)

        # Create content areas
        self.te_directions = QTextEdit()
        self.te_directions.setObjectName("DirectionsTextEdit")
        self.te_directions.setPlaceholderText("Enter cooking directions here...")

        self.te_notes = QTextEdit()
        self.te_notes.setObjectName("NotesTextEdit")
        self.te_notes.setPlaceholderText("Add any additional notes here...")

        # Add components to card
        self.addWidget(self.toggle_container)
        self.addWidget(self.te_directions)
        self.addWidget(self.te_notes)

        # Initially show directions, hide notes
        self.te_notes.hide()

        # Connect signals
        self.btn_directions.clicked.connect(self.show_directions)
        self.btn_notes.clicked.connect(self.show_notes)

    def show_directions(self):
        """Show directions content and update button states."""
        self.te_directions.show()
        self.te_notes.hide()
        self.btn_directions.setObjectName("ToggleButtonActive")
        self.btn_notes.setObjectName("ToggleButtonInactive")
        self._refresh_button_styles()

    def show_notes(self):
        """Show notes content and update button states."""
        self.te_directions.hide()
        self.te_notes.show()
        self.btn_directions.setObjectName("ToggleButtonInactive")
        self.btn_notes.setObjectName("ToggleButtonActive")
        self._refresh_button_styles()

    def _refresh_button_styles(self):
        """Force refresh of button styles after state change."""
        for btn in [self.btn_directions, self.btn_notes]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)


# ── View ────────────────────────────────────────────────────────────────────────────────────────────────────
class AddRecipes(ScrollableNavView):
    """AddRecipes widget for creating new recipes with ingredients and directions."""

    def __init__(self, parent=None):
        # Initialize ViewModels BEFORE calling super().__init__ to avoid initialization order issues
        # This is critical because ScrollableNavView.__init__ calls _build_ui() which needs these attributes
        self.add_recipe_view_model = AddRecipeViewModel()
        self.ingredient_view_model = IngredientViewModel()

        super().__init__(parent)
        self.setObjectName("AddRecipes")

        # register for component-specific styling
        Theme.register_widget(self, Qss.ADD_RECIPE)

        DebugLogger.log("Initializing Add Recipes page", "debug")

        # Connect ViewModel signals
        self._connect_view_model_signals()

        self.stored_ingredients = []
        self._setup_tab_order()

    def showEvent(self, event):
        """When the AddRecipes view is shown, focus the recipe name field."""
        super().showEvent(event)
        # defer to ensure widget is active
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.le_recipe_name.setFocus)

    def _build_ui(self):
        """Setup the UI components for the AddRecipes view."""
        self._create_recipe_details()
        self._create_ingredient_container()
        self._create_directions_notes_card()
        self._create_recipe_image()
        self._create_save_button()
        self._setup_layout()


    # ── UI Components ───────────────────────────────────────────────────────────────────────────────────────────
    def _create_recipe_details(self):
        """Create the recipe details card with form fields."""
        # Recipe Details Card
        self.recipe_details_card = Card(card_type="Default")
        self.recipe_details_card.setHeader("Recipe Info")
        self.recipe_details_card.setSubHeader("Basic information about your recipe.")
        self.recipe_details_card.expandWidth(True)
        self.recipe_form = RecipeForm()  # custom form for recipe details
        self.recipe_details_card.addWidget(self.recipe_form)

        # expose form fields for convenience
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
        self.content_layout.addWidget(self.recipe_details_card) # Recipe details at top
        self.content_layout.addWidget(self.ingredient_container) # Ingredients below details

        # Create directions/notes and image side by side
        column_layout = create_two_column_layout(
            left_widgets=[self.directions_notes_card],
            right_widgets=[self.recipe_image],
            left_weight=2,
            right_weight=1,
            match_heights=True
        )
        self.content_layout.addLayout(column_layout)

        # Add save button with some spacing
        self.content_layout.addSpacing(20)
        self.content_layout.addWidget(self.btn_save, 0, Qt.AlignCenter)

    def _connect_view_model_signals(self):
        """Connect ViewModel signals to UI handlers."""
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


    # ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────
    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        # Connect form change handlers for real-time validation
        self.le_recipe_name.textChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("recipe_name", text))
        self.le_servings.textChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("servings", text))
        self.le_time.textChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("total_time", text))
        self.cb_meal_type.currentTextChanged.connect(lambda text: self.add_recipe_view_model.validate_field_real_time("meal_type", text))

        # Connect recipe name and category for uniqueness checking
        self.le_recipe_name.editingFinished.connect(self._check_recipe_name_uniqueness)
        self.cb_recipe_category.currentTextChanged.connect(self._check_recipe_name_uniqueness)

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


    # ── ViewModel Event Handlers ────────────────────────────────────────────────────────────────────────────
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


    # ── Enhanced Data Binding Event Handlers ────────────────────────────────────────────────────────────────
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

    def _check_recipe_name_uniqueness(self):
        """Check recipe name uniqueness when name or category changes."""
        recipe_name = self.le_recipe_name.text().strip()
        category = self.cb_recipe_category.currentText().strip()

        if recipe_name and category:
            self.add_recipe_view_model.validate_recipe_name(recipe_name, category)


    # ── Business Logic ──────────────────────────────────────────────────────────────────────────────────────
    def _save_recipe(self):
        """
        Collect form data and delegate recipe creation to AddRecipeViewModel.
        Implements proper MVVM pattern by delegating all business logic to ViewModel.
        """
        DebugLogger.log("Starting recipe save process via ViewModel", "debug")

        # Collect raw form data
        raw_form_data = self._collect_form_data()

        # Transform to structured form data using ViewModel
        form_data = self.add_recipe_view_model.preprocess_form_data(raw_form_data)

        # Delegate recipe creation to ViewModel
        self.add_recipe_view_model.create_recipe(form_data)

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

    def _to_payload(self):
        """Legacy method - now replaced by _collect_form_data and ViewModel processing."""
        DebugLogger.log("_to_payload called - consider using ViewModel pattern instead", "warning")
        return self._collect_form_data()

    def _clear_form(self):
        """Clear all form fields after successful save."""
        form_widgets = [
            self.le_recipe_name, self.cb_recipe_category, self.cb_meal_type,
            self.cb_dietary_preference, self.le_time, self.le_servings, self.te_directions
        ]
        clear_form_fields(form_widgets)
        self.recipe_image.clear_default_image()

        # clear stored ingredients and widgets
        self.stored_ingredients.clear()
        self.ingredient_container.clear_all_ingredients()


    # ── Utility Methods ─────────────────────────────────────────────────────────────────────────────────────
    def _display_save_message(self, message: str, success: bool = True):
        """Display a toast notification for save operations."""
        from app.ui.components.widgets import show_toast
        show_toast(self, message, success=success, duration=3000, offset_right=50)

    def _apply_field_error_style(self, field_name: str, error_message: str):
        """Apply error styling to a specific field and show tooltip."""
        field_widget = self._get_field_widget(field_name)
        if field_widget:
            field_widget.setStyleSheet("border: 2px solid #f44336;")  # Material Design error red
            field_widget.setToolTip(error_message)

    def _clear_field_error_style(self, field_name: str):
        """Clear error styling from a specific field."""
        field_widget = self._get_field_widget(field_name)
        if field_widget:
            field_widget.setStyleSheet("")  # Reset to default styling
            field_widget.setToolTip("")

    def _get_field_widget(self, field_name: str):
        """Get the widget reference for a given field name."""
        field_mapping = {
            "recipe_name": self.le_recipe_name,
            "servings": self.le_servings,
            "total_time": self.le_time,
            "meal_type": self.cb_meal_type,
            "recipe_category": self.cb_recipe_category,
            "dietary_preference": self.cb_dietary_preference
        }
        return field_mapping.get(field_name)
