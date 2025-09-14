"""app/ui/pages/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ──
from PySide6.QtCore import Qt

from _dev_tools import DebugLogger
from app.core.dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.recipe_service import RecipeService
from app.core.utils import (
    parse_servings_range,
    safe_int_conversion,
    sanitize_form_input,
    sanitize_multiline_input)
from app.style.icon.config import Name, Type
from app.ui.components.layout.card import Card
from app.ui.components.widgets import Button, RecipeImage
from app.ui.views.base import BaseView
from app.ui.utils import (
    clear_form_fields,
    collect_form_data,
    connect_form_signals,
    create_two_column_layout,
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
        self.btn_save.clicked.connect(self.save_recipe)

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

    def _on_recipe_name_changed(self, recipe_name: str):
        """Update recipe image component when recipe name changes."""
        self.recipe_image.set_recipe_name(recipe_name.strip())

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
