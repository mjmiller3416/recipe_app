"""app/ui/components/forms/add_recipe_form.py

A form for adding new recipes, including fields for recipe details and an image
upload button.
"""

# ── Constants ───────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 60  # fixed height for input fields in the recipe form

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from app.config import MEAL_TYPE, RECIPE_CATEGORIES
from app.ui.components.forms.form_field import ComboBoxField, LineEditField
from app.ui.helpers.ui_helpers import set_fixed_height_for_layout_widgets


# ── Class Definition ────────────────────────────────────────────────────────────
class RecipeForm(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RecipeForm")

        # ── Configure layout ──
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        # create form fields for recipe details
        self.le_recipe_name = LineEditField(
            label_text  = "Recipe Name:",
            placeholder = "Enter recipe name here...",
        )
        self.le_recipe_name.setObjectName("RecipeNameLineEdit")  # for debugging

        self.cb_recipe_category = ComboBoxField(
            label_text = "Category:",
            placeholder = "Select a category...",
            item_list  = RECIPE_CATEGORIES,
        )
        self.cb_recipe_category.setObjectName("RecipeCategoryComboBox")  # for debugging

        self.le_time = LineEditField(
            label_text = "Total Time:",
            placeholder = "e.g. 30 mins...",
        )
        self.le_time.setObjectName("TotalTimeLineEdit")  # for debugging

        self.cb_meal_type = ComboBoxField(
            label_text = "Meal Type:",
            placeholder = "Select a meal type...",
            item_list  = MEAL_TYPE,
        )
        self.cb_meal_type.setObjectName("MealTypeComboBox") # for debugging
        self.le_servings = LineEditField(
            label_text=  "Servings:",
            placeholder="e.g. 4 servings...",
        )

        # add widgets to the form layout
        self._layout.addWidget(self.le_recipe_name, 0, 0, 1, 2)  # row 1
        self._layout.addWidget(self.cb_recipe_category, 1, 0, 1, 1)  # row 2
        self._layout.addWidget(self.le_time, 1, 1, 1, 1)
        self._layout.addWidget(self.cb_meal_type, 2, 0, 1, 1)  # row 3
        self._layout.addWidget(self.le_servings, 2, 1, 1, 1)

        set_fixed_height_for_layout_widgets(
            layout = self._layout,
            height = FIXED_HEIGHT,
            skip   = (QLabel,)
        )
