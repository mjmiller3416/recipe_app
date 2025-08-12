"""app/ui/pages/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QWidget
)

from app.config.config import INT_VALIDATOR, NAME_VALIDATOR
from app.core.dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.recipe_service import RecipeService
from app.style import Theme, Qss
from app.style.icon.config import Type, Name
from app.ui.components.dialogs import MessageDialog
from app.ui.components.forms import IngredientWidget, RecipeForm
from app.ui.components.images.upload_recipe_image import UploadRecipeImage
from app.ui.components.layout.card import Card
from app.ui.components.layout.image_card import ImageCard
from app.ui.components.widgets.button import Button
from app.ui.helpers import clear_error_styles, dynamic_validation
from dev_tools import DebugLogger


# ── Helper Classes ──────────────────────────────────────────────────────────────
class DirectionsNotesCard(Card):
    """Custom card with toggle between Directions and Notes content."""

    def __init__(self, parent=None):
        super().__init__(parent, card_type="Default")
        self.setHeader("Directions & Notes")

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


# ── Class Definition ────────────────────────────────────────────────────────────
class AddRecipes(QWidget):
    """AddRecipes widget for creating new recipes with ingredients and directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipes")

        # register for component-specific styling
        Theme.register_widget(self, Qss.ADD_RECIPE)

        DebugLogger.log("Initializing Add Recipes page", "debug")

        self.ingredient_widgets = []
        self.stored_ingredients = []
        self.selected_image_path = None

        self._build_ui()
        # self._connect_signals()
        self._setup_tab_order()

    def showEvent(self, event):
        """When the AddRecipes view is shown, focus the recipe name field."""
        super().showEvent(event)
        # defer to ensure widget is active
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.le_recipe_name.setFocus)

    def _build_ui(self):
        # main vertical layout
        self.lyt_main = QVBoxLayout(self)
        self.lyt_main.setContentsMargins(20, 20, 20, 20)
        self.lyt_main.setSpacing(16)

        #region ── Recipe Details ──
        # recipe details form wrapped in a Card
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

        self.lyt_main.addWidget(self.recipe_details_card)  # add recipe form card to layout
        #endregion

        # ── Note ─────────────────────────────────────────────────────────────────────────────
        # TODO: reimplement recipe upload and save button
        # logic removed from layout -- remains in file for reference
        # buttons
        # self.lyt_buttons =QVBoxLayout()  # vertical layout for buttons
        #
        # upload image button
        # self.btn_upload_image = UploadRecipeImage()
        # self.btn_upload_image.setObjectName("UploadRecipeImage")
        # self.lyt_buttons.addWidget(
        #     self.btn_upload_image)  # add upload image button to buttons layout

        # save button
        # self.btn_save = QPushButton("Save Recipe")
        # self.btn_save.setObjectName("SaveButton")
        # self.btn_save.setFixedHeight(50)  # set fixed height for consistency
        # ─────────────────────────────────────────────────────────────────────────────────────


        #region ── Ingredients Card ──
        self.ingredients_card = Card(card_type="Default")
        self.ingredients_card.setHeader("Ingredients")
        self.ingredients_card.setSubHeader("List of ingredients for the recipe.")
        self.ingredients_card.expandWidth(True)
        self.lyt_main.addWidget(self.ingredients_card)  # add left section to main content layout
        #endregion

        #region ── Directions & Notes Card ──
        self.directions_notes_card = DirectionsNotesCard()
        self.directions_notes_card.expandBoth(True)


        # Expose text edits for convenience (for form validation, saving, etc.)
        self.te_directions = self.directions_notes_card.te_directions
        self.te_notes = self.directions_notes_card.te_notes
        #endregion

        #region ── Image Card ──
        self.image_card = ImageCard()
        self.image_card.setHeader("Recipe Image")
        self.image_card.setSubHeader("Upload an image of your recipe.")
        self.image_card.addButton("Upload Image")
        #endregion

        # hbox layout for directions and image
        self.h = QHBoxLayout()
        self.h.addWidget(self.directions_notes_card)
        self.h.addWidget(self.image_card)
        self.lyt_main.addLayout(self.h)

    """ def _connect_signals(self):
        self.btn_save.clicked.connect(self.save_recipe)
        self.btn_upload_image.image_uploaded.connect(self._update_image_path)

        dynamic_validation(self.le_recipe_name, NAME_VALIDATOR)
        dynamic_validation(self.le_servings, INT_VALIDATOR)

        self.cb_recipe_category.selection_validated.connect(lambda: clear_error_styles(self.cb_recipe_category))
        self.cb_meal_type.selection_validated.connect(lambda: clear_error_styles(self.cb_meal_type))
        self.te_directions.textChanged.connect(lambda: clear_error_styles(self.te_directions)) """

    def _setup_tab_order(self):
        """Define a fixed tab order for keyboard navigation."""
        from PySide6.QtWidgets import QWidget

        # basic recipe fields
        QWidget.setTabOrder(self.le_recipe_name, self.le_time)
        QWidget.setTabOrder(self.le_time, self.le_servings)
        QWidget.setTabOrder(self.le_servings, self.cb_meal_type)
        QWidget.setTabOrder(self.cb_meal_type, self.cb_recipe_category)
        QWidget.setTabOrder(self.cb_recipe_category, self.cb_dietary_preference)
        # ingredients - chain through the first ingredient widget if it exists
        if self.ingredient_widgets:
            w = self.ingredient_widgets[0]
            QWidget.setTabOrder(self.le_servings, w.le_quantity)
            QWidget.setTabOrder(w.le_quantity, w.cb_unit)
            QWidget.setTabOrder(w.cb_unit, w.sle_ingredient_name)
            QWidget.setTabOrder(w.sle_ingredient_name, w.cb_ingredient_category)
            QWidget.setTabOrder(w.cb_ingredient_category, w.btn_ico_subtract)
            QWidget.setTabOrder(w.btn_ico_subtract, w.btn_ico_add)
            # then to directions
            QWidget.setTabOrder(w.btn_ico_add, self.te_directions)

    def _add_ingredient(self, removable=True):
        widget = IngredientWidget(removable=removable)

        widget.remove_ingredient_requested.connect(self._remove_ingredient)
        widget.add_ingredient_requested.connect(self._add_ingredient)
        widget.ingredient_validated.connect(self._store_ingredient)
        self.ingredient_widgets.append(widget)
        self.ingredients_card.addWidget(widget)

    def _remove_ingredient(self, widget):
        """Remove the specified ingredient widget from the card."""
        self.ingredients_card.removeWidget(widget)
        widget.deleteLater()
        self.ingredients_card.update()
        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)

    def _store_ingredient(self, data):
        self.stored_ingredients.append(data)

    def _update_image_path(self, image_path: str):
        """Update the selected image path when an image is selected."""
        self.selected_image_path = image_path if image_path else None

    def save_recipe(self):
        """
        Gathers all form data (recipe fields + ingredient widgets),
        constructs a RecipeCreateDTO, and hands it to RecipeService.
        """
        # ── payload recipe data ──
        recipe_data = self.to_payload()

        # ── payload raw ingredients ──
        raw_ingredients = [
            widget.to_payload()
            for widget in self.ingredient_widgets
        ]

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
            MessageDialog(
                "warning",
                "Invalid Recipe Data",
                "Your recipe form is missing something required or has an invalid value. Please review all fields.",
                self
            ).exec()
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
        self._display_save_message(
            f"Recipe '{new_recipe.recipe_name}' saved successfully!",
            success=True
        )

        # ── clear form and reset state ──
        self._clear_form()
        self.stored_ingredients.clear()
        for widget in self.ingredient_widgets:
            container = widget.parent()
            if container:
                container.deleteLater()
        self.ingredient_widgets = []

    def to_payload(self):
        """Collect all recipe form data and return it as a dict for API calls."""
        return {
            "recipe_name":         self.le_recipe_name.text().strip(),
            "recipe_category":     self.cb_recipe_category.currentText().strip(),
            "meal_type":           self.cb_meal_type.currentText().strip(),
            "dietary_preference": self.cb_dietary_preference.currentText().strip(),
            "total_time":          int(self.le_time.text().strip() or 0),
            "servings":            int(self.le_servings.text().strip() or 0),
            "directions":          self.te_directions.toPlainText().strip(),
            "image_path":          self.selected_image_path or "",
        }

    def _clear_form(self):
        """Clear all form fields after successful save."""
        self.le_recipe_name.clear()
        self.cb_recipe_category.setCurrentIndex(-1)
        self.cb_meal_type.setCurrentIndex(-1)
        self.cb_dietary_preference.setCurrentIndex(-1)
        self.le_time.clear()
        self.le_servings.clear()
        self.te_directions.clear()
        self.btn_upload_image.clear_image()
        self.selected_image_path = None

        # clear stored ingredients and widgets
        self.stored_ingredients.clear()
        for widget in self.ingredient_widgets:
            container = widget.parent()
            self.ingredients_card.removeWidget(container)
            container.deleteLater()
        self.ingredient_widgets.clear()

        # add back the initial ingredient widget
        self._add_ingredient(removable=False)
