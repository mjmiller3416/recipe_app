"""app/ui/pages/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ──
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QTextEdit, QWidget
from app.config import (
    DIETARY_PREFERENCES,
    FLOAT_VALIDATOR,
    INGREDIENT_CATEGORIES,
    MEAL_TYPE,
    MEASUREMENT_UNITS,
    NAME_PATTERN,
    RECIPE_CATEGORIES)
from app.core.database.db import create_session
from app.core.dtos import IngredientSearchDTO, RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.ingredient_service import IngredientService
from app.core.services.recipe_service import RecipeService
from app.core.utils import (
    parse_servings_range,
    safe_float_conversion,
    safe_int_conversion,
    sanitize_form_input,
    sanitize_multiline_input)
from app.style import Qss, Theme
from app.style.icon.config import Name, Type
from app.ui.components.images import RecipeImage
from app.ui.components.inputs import SmartLineEdit
from app.ui.components.layout.card import ActionCard, Card
from app.ui.components.widgets import ComboBox, ToolButton
from app.ui.components.widgets.button import Button
from app.ui.utils import (
    batch_connect_signals,
    clear_error_styles,
    clear_form_fields,
    collect_form_data,
    connect_form_signals,
    create_labeled_form_grid,
    dynamic_validation,
    setup_main_scroll_layout,
    setup_tab_order_chain,
    validate_required_fields,
    create_two_column_layout)
from _dev_tools import DebugLogger


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


# ── Ingredient Form ─────────────────────────────────────────────────────────────────────────────────────────
class IngredientForm(QWidget):
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)

    def __init__(self, removable=True, parent=None):
        """
        Initializes the IngredientForm with a grid layout and sets up UI components.
        The ingredient name input is an editable ComboBox populated with existing
        ingredient names. Selecting an existing ingredient auto-populates its category.

        Args:
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
        # Initialize IngredientService with a new DB session
        self._session = create_session()
        self.ingredient_service = IngredientService(self._session)
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

        # Ingredient name field - expandable
        all_ingredient_names = self.ingredient_service.list_distinct_names()
        self.sle_ingredient_name = SmartLineEdit(
            list_items=all_ingredient_names,
            placeholder="Ingredient Name"
        )
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

        self.sle_ingredient_name.currentTextChanged.connect(self._ingredient_name_changed) # connect new signal

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
            clear_error_styles(self.sle_ingredient_name)  # SmartLineEdit is now a QLineEdit
            return

        # validate the ingredient name against the NAME_PATTERN
        if not NAME_PATTERN.match(current_text):
            self.sle_ingredient_name.setStyleSheet("border: 1px solid red;")
            return
        else:
            clear_error_styles(self.sle_ingredient_name)

        search_dto = IngredientSearchDTO(search_term=current_text)
        matching_ingredients = self.ingredient_service.find_matching_ingredients(search_dto)

        exact_match = None
        for ingredient in matching_ingredients:
            if ingredient.ingredient_name.lower() == current_text.lower():
                exact_match = ingredient
                self.exact_match = exact_match
                break

        if exact_match:
            category_index = self.cb_ingredient_category.findText(
                exact_match.ingredient_category,
                Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive,
            )

            if category_index < 0:
                category_index = self.cb_ingredient_category.findText(
                    exact_match.ingredient_category,
                    Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchContains,
                )

            if category_index >= 0:
                self.cb_ingredient_category.setCurrentIndex(category_index)
            else:
                self.cb_ingredient_category.addItem(exact_match.ingredient_category)
                self.cb_ingredient_category.setCurrentText(exact_match.ingredient_category)

            clear_error_styles(self.cb_ingredient_category)
        else:
            self.cb_ingredient_category.setCurrentIndex(-1)
            self.cb_ingredient_category.setEnabled(True)

    def get_ingredient_data(self) -> dict:
        """Returns the ingredient data as a dictionary for external collection."""
        return self.to_payload()

    def request_removal(self):
        """Emits a signal to request removal of this ingredient widget."""
        if self.parent() and len(self.parent().findChildren(IngredientForm)) > 1:
            self.remove_ingredient_requested.emit(self)

    def to_payload(self) -> dict:
        """Returns a plain dict that matches RecipeIngredientDTO fields"""
        return {
        "ingredient_name": sanitize_form_input(self.sle_ingredient_name.text()),
        "ingredient_category": sanitize_form_input(self.cb_ingredient_category.currentText()),
        "unit": sanitize_form_input(self.cb_unit.currentText()),
        "quantity": safe_float_conversion(self.le_quantity.text().strip()),
        "existing_ingredient_id": self.exact_match.id if self.exact_match else None,
        }


# ── Ingredients Card ────────────────────────────────────────────────────────────────────────────────────────
class IngredientsCard(ActionCard):
    """
    Container for managing ingredient widgets within a Card.
    Provides add/remove functionality and data collection.
    """

    ingredients_changed = Signal()  # Emitted when ingredients are added/removed

    def __init__(self, parent=None):
        """Initialize the ingredient container."""
        super().__init__(card_type="Default", parent=parent)

        self.setHeader("Ingredients")
        self.setSubHeader("List all the ingredients required for this recipe.")

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
        ingredient_widget = IngredientForm()
        ingredient_widget.remove_ingredient_requested.connect(self._remove_ingredient_widget)

        self.ingredient_widgets.append(ingredient_widget)
        self.addWidget(ingredient_widget)

        self.ingredients_changed.emit()

    def _remove_ingredient_widget(self, widget: IngredientForm):
        """Remove an ingredient widget from the container."""
        if len(self.ingredient_widgets) <= 1:
            return  # Always keep at least one ingredient widget

        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)
            self.removeWidget(widget)
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
        """Clear all ingredient widgets and add one empty one."""
        # Remove all existing widgets
        for widget in self.ingredient_widgets:
            self.removeWidget(widget)
            widget.deleteLater()

        self.ingredient_widgets.clear()

        # Add one fresh ingredient widget
        self._add_ingredient_widget()

    def get_ingredient_count(self) -> int:
        """Get the number of ingredient widgets."""
        return len(self.ingredient_widgets)


# ── Direction & Notes Card ──────────────────────────────────────────────────────────────────────────────────
class DirectionsNotesCard(Card):
    """Custom card with toggle between Directions and Notes content."""

    def __init__(self, parent=None):
        super().__init__(card_type="Default")
        self.setHeader("Directions & Notes")
        self.setMinimumHeight(600)  # set minimum height to ensure enough space for content

        # Create toggle buttons container
        self.toggle_container = QWidget()
        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
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


# ── Add Recipes View ────────────────────────────────────────────────────────────────────────────────────────
class AddRecipes(QWidget):
    """AddRecipes widget for creating new recipes with ingredients and directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipes")

        # register for component-specific styling
        Theme.register_widget(self, Qss.ADD_RECIPE)

        DebugLogger.log("Initializing Add Recipes page", "debug")

        self.stored_ingredients = []

        self._build_ui()
        self._connect_signals()
        self._setup_tab_order()

    def showEvent(self, event):
        """When the AddRecipes view is shown, focus the recipe name field."""
        super().showEvent(event)
        # defer to ensure widget is active
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.le_recipe_name.setFocus)

    def _build_ui(self):
        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

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

        self.scroll_layout.addWidget(self.recipe_details_card)  # add recipe form card to layout

        # Ingredients Container
        self.ingredient_container = IngredientsCard()
        self.ingredient_container.expandWidth(True)
        self.scroll_layout.addWidget(self.ingredient_container)

        # Directions & Notes Card
        self.directions_notes_card = DirectionsNotesCard()
        self.directions_notes_card.expandBoth(True)


        # Expose text edits for convenience (for form validation, saving, etc.)
        self.te_directions = self.directions_notes_card.te_directions
        self.te_notes = self.directions_notes_card.te_notes

        # Recipe Image
        self.recipe_image = RecipeImage()

        # Add directions and image using shadow-safe utility
        create_two_column_layout(
            self.scroll_layout,
            self.directions_notes_card,
            self.recipe_image,
            left_proportion=2,
            right_proportion=1,
            match_heights=True
        )

        # ── Save Button ──
        self.btn_save = Button("Save Recipe", Type.PRIMARY, Name.SAVE)
        self.btn_save.setObjectName("SaveRecipeButton")
        self.btn_save.clicked.connect(self.save_recipe)

        # Add save button with some spacing
        self.scroll_layout.addSpacing(20)
        self.scroll_layout.addWidget(self.btn_save, 0, Qt.AlignCenter)

    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        # Connect form change handlers
        form_change_handlers = {
            "recipe_name": self._on_recipe_name_changed
        }
        form_widgets = {
            "recipe_name": self.le_recipe_name
        }
        connect_form_signals(form_widgets, form_change_handlers)

        # Batch connect remaining signals
        signal_connections = [
            (self.recipe_image.generate_image_requested, self._on_generate_default_image_requested),
            (self.recipe_image.image_selected, self._on_image_selected)
        ]
        batch_connect_signals(signal_connections)

        # Connect AI service signals for async operations
        """ self.ai_service.generation_finished.connect(self._on_generation_finished)
        self.ai_service.generation_failed.connect(self._on_generation_failed) """

    def _on_recipe_name_changed(self, recipe_name: str):
        """Update recipe image component when recipe name changes."""
        self.recipe_image.set_recipe_name(recipe_name.strip())

    def _on_generate_default_image_requested(self, recipe_name: str):
        """Handle AI default image generation request (now async)."""
        if not self.ai_service.is_available():
            DebugLogger().log("AI Image Generation service not available", "error")
            self.recipe_image.reset_generate_button()
            return

        # Start async default image generation (non-blocking)
        self.ai_service.generate_default_image_async(recipe_name)
        DebugLogger().log(f"Started background default image generation for '{recipe_name}'", "info")

    def _on_generation_finished(self, recipe_name: str, result):
        """Handle successful image generation completion."""
        # Reset the UI state
        self.recipe_image.reset_generate_button()

        if result:
            DebugLogger().log(f"Background generation completed for '{recipe_name}' - image saved", "info")

            # Handle single image result (string path)
            if isinstance(result, str):
                image_path = result
                DebugLogger().log(f"Single image generated: {image_path}", "info")
                # Set the default image
                self.recipe_image.set_reference_image_path(image_path)
                # Also update selected path for saving
                self.selected_image_path = image_path

            # Handle dual image result (ImagePairPaths) for backward compatibility
            elif hasattr(result, 'portrait_path') and result.portrait_path:
                portrait_path = str(result.portrait_path)
                DebugLogger().log(f"Portrait image from pair: {portrait_path}", "info")
                # Set the default image to the portrait
                self.recipe_image.set_reference_image_path(portrait_path)
                # Also update selected path for saving
                self.selected_image_path = portrait_path

    def _on_generation_failed(self, recipe_name: str, error_msg: str):
        """Handle image generation failure."""
        # Reset the UI state
        self.recipe_image.reset_generate_button()
        DebugLogger().log(f"Background generation failed for '{recipe_name}': {error_msg}", "error")

    def _on_image_selected(self, image_path: str):
        """Handle image selection from the gallery."""
        self.selected_image_path = image_path

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

    def _update_image_path(self, image_path: str):
        """Update the selected image path when an image is selected."""
        self.selected_image_path = image_path if image_path else None

    def save_recipe(self):
        """
        Gathers all form data (recipe fields + ingredient widgets),
        constructs a RecipeCreateDTO, and hands it to RecipeService.
        """
        # ── validate required fields ──
        required_fields = {
            "Recipe Name": self.le_recipe_name,
            "Meal Type": self.cb_meal_type,
            "Servings": self.le_servings
        }
        is_valid, validation_errors = validate_required_fields(required_fields)
        if not is_valid:
            error_msg = "Please fix the following errors:\n• " + "\n• ".join(validation_errors)
            self._display_save_message(error_msg, success=False)
            return

        # ── payload recipe data ──
        recipe_data = self.to_payload()

        # ── payload raw ingredients ──
        raw_ingredients = self.ingredient_container.get_all_ingredients_data()

        # ── convert raw_ingredients ──
        try:
            ingredient_dtos = [
                RecipeIngredientDTO(
                    ingredient_name=data["ingredient_name"],
                    ingredient_category=data["ingredient_category"],
                    quantity=data["quantity"],
                    unit=data["unit"],
                )
                for data in raw_ingredients
            ]
        except Exception as dto_err:
            DebugLogger().log(f"[AddRecipes] DTO construction failed: {dto_err}", "error")
            return  # show error dialog

        # ── convert recipe_data ──
        try:
            recipe_dto = RecipeCreateDTO(
                **recipe_data,
                ingredients=ingredient_dtos,
            )
        except Exception as dto_err:
            DebugLogger().log(f"[AddRecipes] RecipeCreateDTO validation failed: {dto_err}", "error")
            return

        # ── create recipe via service (internal session management) ──
        service = RecipeService()
        try:
            new_recipe = service.create_recipe_with_ingredients(recipe_dto)
        except Exception as svc_err:
            DebugLogger().log(f"[AddRecipes.save_recipe] Error saving recipe: {svc_err}", "error")
            self._display_save_message(
                f"Failed to save recipe: {svc_err}", success=False
            )
            return

        # ── success! ──
        DebugLogger().log(f"[AddRecipes] Recipe '{new_recipe.recipe_name}' saved with ID={new_recipe.id}", "info")

        # Update recipe with selected image path if available
        selected_image = self.recipe_image.get_reference_image_path()
        DebugLogger().log(f"[AddRecipes] get_reference_image_path returned: '{selected_image}'", "info")
        if selected_image:
            try:
                service.update_recipe_reference_image_path(new_recipe.id, selected_image)
                DebugLogger().log(f"[AddRecipes] Updated recipe {new_recipe.id} with default image: {selected_image}", "info")
            except Exception as img_err:
                DebugLogger().log(f"[AddRecipes] Failed to update recipe default image: {img_err}", "warning")
        else:
            DebugLogger().log(f"[AddRecipes] No selected image to update for recipe {new_recipe.id}", "info")

        self._display_save_message(
            f"Recipe '{new_recipe.recipe_name}' saved successfully!",
            success=True
        )

        # ── clear form and reset state ──
        self._clear_form()
        self.stored_ingredients.clear()
        self.ingredient_container.clear_all_ingredients()

    def to_payload(self):
        """Collect all recipe form data and return it as a dict for API calls."""
        form_mapping = {
            "recipe_name": self.le_recipe_name,
            "recipe_category": self.cb_recipe_category,
            "meal_type": self.cb_meal_type,
            "dietary_preference": self.cb_dietary_preference,
            "total_time": self.le_time,
            "servings": self.le_servings,
            "directions": self.te_directions
        }
        data = collect_form_data(form_mapping)

        # Apply text sanitization
        data["recipe_name"] = sanitize_form_input(data["recipe_name"])
        data["recipe_category"] = sanitize_form_input(data["recipe_category"])
        data["meal_type"] = sanitize_form_input(data["meal_type"])
        data["dietary_preference"] = sanitize_form_input(data["dietary_preference"])
        data["directions"] = sanitize_multiline_input(data["directions"])

        # Apply transformations for servings/time parsing
        data["total_time"] = safe_int_conversion(data["total_time"])
        data["servings"] = parse_servings_range(data["servings"])
        data["reference_image_path"] = self.recipe_image.get_reference_image_path() or ""

        return data

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

    def _display_save_message(self, message: str, success: bool = True):
        """Display a toast notification for save operations."""
        from app.ui.components.widgets import show_toast
        show_toast(self, message, success=success, duration=3000, offset_right=50)
