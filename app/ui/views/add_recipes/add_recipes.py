"""app/ui/pages/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ──
from PySide6.QtCore import Qt

from _dev_tools import DebugLogger
from app.core.dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.recipe_service import RecipeService
from app.core.services.ai_gen.background_manager import get_background_manager
from app.core.utils import (
    parse_servings_range,
    safe_int_conversion,
    sanitize_form_input,
    sanitize_multiline_input)
from app.style.icon.config import Name, Type
from app.ui.components.layout.card import Card
from app.ui.components.widgets import Button
from app.ui.views.base import BaseView
from app.ui.utils import (
    clear_form_fields,
    collect_form_data,
    connect_form_signals,
    setup_tab_order_chain,
    validate_required_fields)
from ._recipe_form import RecipeForm
from ._ingredients_card import IngredientsCard
from ._directions_notes_card import DirectionsNotesCard


class AddRecipes(BaseView):
    """AddRecipes widget for creating new recipes with ingredients and directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipes")

        DebugLogger.log("Initializing Add Recipes page", "debug")

        self.stored_ingredients = []
        self.last_focused_widget = None  # Track last focused widget
        self.tab_order_widgets = []  # Store tab order for reference

        self._build_ui()
        self._connect_signals()
        self._setup_tab_order()


    # ── Private ──
    def _build_ui(self):
        """Set up the main UI layout and components."""
        self._create_cards()
        self._create_recipe_form()
        self._create_save_button()

    def _create_cards(self):
        """Create the main cards for the AddRecipes view."""
        # Recipe Details Card
        self.recipe_details_card = Card(card_type="Default")
        self.recipe_details_card.setHeader("Recipe Info")
        self.recipe_details_card.setSubHeader("Basic information about your recipe.")
        self.recipe_details_card.expandWidth(True)
        self.content_layout.addWidget(self.recipe_details_card)

        # Create Ingredients Card
        self.ingredient_container = IngredientsCard()
        self.ingredient_container.expandWidth(True)
        self.content_layout.addWidget(self.ingredient_container)

        # Directions & Notes Card
        self.directions_notes_card = DirectionsNotesCard()
        self.directions_notes_card.expandBoth(True)
        self.content_layout.addWidget(self.directions_notes_card)

        # expose text edits for convenience
        self.te_directions = self.directions_notes_card.te_directions
        self.te_notes = self.directions_notes_card.te_notes

    def _create_recipe_form(self):
        """Create the recipe details."""
        # Create Recipe Form
        self.recipe_form = RecipeForm()  # custom form for recipe details
        self.recipe_details_card.addWidget(self.recipe_form)

        # expose form fields for convenience
        self.le_recipe_name = self.recipe_form.le_recipe_name
        self.cb_recipe_category = self.recipe_form.cb_recipe_category
        self.le_time = self.recipe_form.le_time
        self.cb_meal_type = self.recipe_form.cb_meal_type
        self.cb_dietary_preference = self.recipe_form.cb_dietary_preference
        self.le_servings = self.recipe_form.le_servings

    def _create_save_button(self):
        """Create the save button at the bottom of the scroll area."""
        self.btn_save = Button("Save Recipe", Type.PRIMARY, Name.SAVE)
        self.btn_save.setObjectName("SaveRecipeButton")
        self.btn_save.clicked.connect(self._save_recipe)

        # Add save button with some spacing
        self.content_layout.addSpacing(20)
        self.content_layout.addWidget(self.btn_save, 0, Qt.AlignCenter)

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

        # Update tab order when ingredients change
        self.ingredient_container.ingredients_changed.connect(self._on_ingredients_changed)

    def _on_ingredients_changed(self):
        """Handle changes in the ingredient list to update tab order."""
        self._setup_tab_order()

    def _on_recipe_name_changed(self, recipe_name: str):
        """Handle recipe name changes."""
        # Note: recipe_image component was removed, this is now a placeholder
        pass

    def _setup_tab_order(self):
        """Define a fixed tab order for keyboard navigation."""
        # Recipe form widgets
        base_widgets = [
            self.le_recipe_name,
            self.le_time,
            self.le_servings,
            self.cb_meal_type,
            self.cb_recipe_category,
            self.cb_dietary_preference
        ]

        # Add all ingredient widgets with correct order
        for widget in self.ingredient_container.ingredient_widgets:
            ingredient_chain = [
                widget.cb_unit,
                widget.le_quantity,
                widget.sle_ingredient_name,
                widget.cb_ingredient_category,
            ]
            base_widgets.extend(ingredient_chain)

        # Add the "Add Ingredient" button
        if self.ingredient_container.button:
            base_widgets.append(self.ingredient_container.button)

        # Add Directions/Notes toggle and text areas
        base_widgets.extend([
            self.directions_notes_card.btn_directions,
            self.directions_notes_card.btn_notes,
            self.te_directions
        ])

        # Add save button
        base_widgets.append(self.btn_save)

        # Store the tab order for reference
        self.tab_order_widgets = [w for w in base_widgets if w is not None]

        for widget in self.tab_order_widgets:
            if widget and widget.__class__.__name__ == 'ComboBox':
                # Install on the line_edit and button children too
                if hasattr(widget, 'line_edit'):
                    widget.line_edit.installEventFilter(self)
                if hasattr(widget, 'cb_btn'):
                    widget.cb_btn.installEventFilter(self)

        setup_tab_order_chain(base_widgets)
        self.setFocusPolicy(Qt.StrongFocus)

        DebugLogger.log(f"Tab order setup with {len(self.tab_order_widgets)} widgets", "debug")

    def _initialize_focus(self):
        """Initialize focus when view is shown."""
        if self.le_recipe_name:
            self.le_recipe_name.setFocus()
            self.last_focused_widget = self.le_recipe_name

    def _save_recipe(self):
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
        recipe_data = self._to_payload()

        # ── payload raw ingredients ──
        raw_ingredients = self.ingredient_container.getAllIngredientsData()

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

        # ── trigger background AI image generation ──
        try:
            manager = get_background_manager()
            reference_path, banner_path = manager.generate_recipe_images(
                new_recipe.id,
                new_recipe.recipe_name
            )

            # Update recipe with predicted paths immediately
            service.update_recipe_reference_image_path(new_recipe.id, reference_path)
            service.update_recipe_banner_image_path(new_recipe.id, banner_path)

            DebugLogger().log(
                f"[AddRecipes] Started background image generation for recipe {new_recipe.id}",
                "info"
            )

            # Show user notification about image generation
            from app.ui.components.widgets import show_toast
            show_toast(
                self,
                "Generating AI images for your recipe...",
                success=True,
                duration=2000,
                offset_right=50
            )
        except Exception as img_err:
            DebugLogger().log(
                f"[AddRecipes] Failed to start image generation: {img_err}",
                "warning"
            )

        self._display_save_message(
            f"Recipe '{new_recipe.recipe_name}' saved successfully!",
            success=True
        )

        # ── clear form and reset state ──
        self._clear_form()
        self.stored_ingredients.clear()
        self.ingredient_container.clearAllIngredients()

    def _to_payload(self):
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
        # Don't include reference_image_path in payload - will be generated async

        return data

    def _clear_form(self):
        """Clear all form fields after successful save."""
        form_widgets = [
            self.le_recipe_name, self.cb_recipe_category, self.cb_meal_type,
            self.cb_dietary_preference, self.le_time, self.le_servings, self.te_directions
        ]
        clear_form_fields(form_widgets)

        # clear stored ingredients and widgets
        self.stored_ingredients.clear()
        self.ingredient_container.clearAllIngredients()

        # Reset focus tracking
        self.last_focused_widget = self.le_recipe_name

        # Since ingredients were cleared, rebuild tab order
        self._setup_tab_order()

    def _display_save_message(self, message: str, success: bool = True):
        """Display a toast notification for save operations."""
        from app.ui.components.widgets import show_toast
        show_toast(self, message, success=success, duration=3000, offset_right=50)

    def _on_widget_focused(self, widget):
        """Handle focus change from any widget in the application."""
        # Only track widgets that are in our tab order
        if widget in self.tab_order_widgets:
            self.last_focused_widget = widget
            DebugLogger.log(f"Focus tracked: {widget.__class__.__name__} - {widget.objectName()}", "debug")

    # ── Event Handling ──
    def eventFilter(self, watched, event):
        """Track focus changes on widgets."""
        from PySide6.QtCore import QEvent

        # Track both focus events AND mouse clicks
        if event.type() == QEvent.FocusIn:
            # Update last focused widget for ANY widget
            if watched in self.tab_order_widgets:
                self.last_focused_widget = watched
                DebugLogger.log(f"Focus tracked via FocusIn: {watched.__class__.__name__}", "debug")

        elif event.type() == QEvent.MouseButtonPress:
            # For ComboBox widgets, clicking anywhere on them should track focus
            if watched in self.tab_order_widgets:
                self.last_focused_widget = watched
                DebugLogger.log(f"Focus tracked via MousePress: {watched.__class__.__name__}", "debug")
                # Force the widget to take focus
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, watched.setFocus)
            else:
                # Check if this is a child of a ComboBox in our tab order
                parent = watched.parent()
                while parent:
                    if parent in self.tab_order_widgets and parent.__class__.__name__ == 'ComboBox':
                        self.last_focused_widget = parent
                        DebugLogger.log(f"Focus tracked via MousePress on ComboBox child: {parent.__class__.__name__}", "debug")
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(0, parent.setFocus)
                        break
                    parent = parent.parent()

        # Check for new ingredient widgets
        if event.type() == QEvent.FocusIn and watched not in self.tab_order_widgets:
            for ingredient_widget in self.ingredient_container.ingredient_widgets:
                if watched in [ingredient_widget.cb_unit,
                            ingredient_widget.le_quantity,
                            ingredient_widget.sle_ingredient_name,
                            ingredient_widget.cb_ingredient_category]:
                    DebugLogger.log(f"New ingredient widget detected, updating tab order", "debug")
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, self._setup_tab_order)
                    break

        return super().eventFilter(watched, event)

    def focusInEvent(self, event):
        """Handle focus returning to the form container."""
        super().focusInEvent(event)

        from PySide6.QtCore import Qt, QTimer

        # Debug log
        DebugLogger.log(f"Form focusInEvent - reason: {event.reason()}, last_focused: {self.last_focused_widget}", "debug")

        # For any tab focus reason, restore to last widget or first widget
        if event.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            # Defer focus setting to avoid conflicts
            if event.reason() == Qt.BacktabFocusReason:
                # Backtab - go to last widget or end of list
                target = self.last_focused_widget if self.last_focused_widget in self.tab_order_widgets else (
                    self.tab_order_widgets[-1] if self.tab_order_widgets else None
                )
            else:
                # Normal tab - go to last widget or beginning
                target = self.last_focused_widget if self.last_focused_widget in self.tab_order_widgets else (
                    self.tab_order_widgets[0] if self.tab_order_widgets else None
                )

            if target:
                QTimer.singleShot(0, lambda: target.setFocus(event.reason()))

    def focusNextPrevChild(self, next):
        """Override to ensure tab navigation stays within our defined order."""
        from PySide6.QtWidgets import QApplication

        current_widget = QApplication.focusWidget()

        # If no current focus or not in our tab order, handle specially
        if not current_widget or current_widget not in self.tab_order_widgets:
            if self.tab_order_widgets:
                if next:
                    # Tab forward - use last focused or first widget
                    target = self.last_focused_widget if self.last_focused_widget in self.tab_order_widgets else self.tab_order_widgets[0]
                else:
                    # Tab backward - use last focused or last widget
                    target = self.last_focused_widget if self.last_focused_widget in self.tab_order_widgets else self.tab_order_widgets[-1]

                target.setFocus(Qt.TabFocusReason if next else Qt.BacktabFocusReason)
                return True

        # If current widget is in our tab order, navigate within it
        if current_widget in self.tab_order_widgets:
            try:
                current_index = self.tab_order_widgets.index(current_widget)

                if next:
                    # Moving forward
                    next_index = (current_index + 1) % len(self.tab_order_widgets)
                else:
                    # Moving backward
                    next_index = (current_index - 1) % len(self.tab_order_widgets)

                next_widget = self.tab_order_widgets[next_index]
                if next_widget and next_widget.isVisible() and next_widget.isEnabled():
                    next_widget.setFocus(Qt.TabFocusReason if next else Qt.BacktabFocusReason)
                    return True
            except (ValueError, IndexError):
                pass

        # Fall back to default behavior
        return super().focusNextPrevChild(next)

    def keyPressEvent(self, event):
        """Handle key press events at the form level."""
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        # Check for Tab/Backtab when form itself has focus
        if event.key() in (Qt.Key_Tab, Qt.Key_Backtab):
            focused_widget = QApplication.focusWidget()

            # If the form itself has focus (not a child widget)
            if focused_widget == self or focused_widget is None:
                if self.tab_order_widgets:
                    if event.key() == Qt.Key_Tab:
                        # Forward tab
                        target = self.last_focused_widget if self.last_focused_widget in self.tab_order_widgets else self.tab_order_widgets[0]
                    else:
                        # Backward tab
                        target = self.last_focused_widget if self.last_focused_widget in self.tab_order_widgets else self.tab_order_widgets[-1]

                    target.setFocus(Qt.TabFocusReason if event.key() == Qt.Key_Tab else Qt.BacktabFocusReason)
                    event.accept()
                    return

        # Handle Shift+Tab as Backtab
        if event.key() == Qt.Key_Tab and event.modifiers() == Qt.ShiftModifier:
            # Convert to backtab
            self.focusNextPrevChild(False)
            event.accept()
            return

        super().keyPressEvent(event)

    def showEvent(self, event):
        """When the AddRecipes view is shown, focus the recipe name field."""
        super().showEvent(event)
        from PySide6.QtCore import QTimer

        # Set initial focus and tracking
        QTimer.singleShot(0, lambda: self._initialize_focus())
