"""app/ui/components/forms/add_recipe_form.py

A form for adding new recipes, including fields for recipe details and an image
upload button.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget, QLineEdit, QVBoxLayout

from app.config import MEAL_TYPE, RECIPE_CATEGORIES, DIETARY_PREFERENCES
from app.ui.components.widgets import ComboBox
from app.ui.helpers.ui_helpers import set_fixed_height_for_layout_widgets

# ── Constants ───────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 60  # fixed height for input fields in the recipe form


# ── Recipe Form ──────────────────────────────────────────────────────────────────────────────
class RecipeForm(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RecipeForm")

        # ── Configure layout ──
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        # create labels and inputs for recipe details - labels above inputs
        # Recipe Name (full width)
        self.lbl_recipe_name = QLabel("Recipe Name")
        self.le_recipe_name = QLineEdit()
        self.le_recipe_name.setPlaceholderText("e.g. Spaghetti Carbonara")
        self.le_recipe_name.setObjectName("RecipeNameLineEdit")

        # Total Time
        self.lbl_time = QLabel("Total Time")
        self.le_time = QLineEdit()
        self.le_time.setPlaceholderText("e.g. 30 mins")
        self.le_time.setObjectName("TotalTimeLineEdit")

        # Servings
        self.lbl_servings = QLabel("Servings")
        self.le_servings = QLineEdit()
        self.le_servings.setPlaceholderText("e.g. 4")
        self.le_servings.setObjectName("ServingsLineEdit")

        # Meal Type
        self.lbl_meal_type = QLabel("Meal Type")
        self.cb_meal_type = ComboBox(list_items=MEAL_TYPE, placeholder="Select meal type")
        self.cb_meal_type.setObjectName("ComboBox")
        self.cb_meal_type.setProperty("context", "recipe_form")

        # Category
        self.lbl_category = QLabel("Category")
        self.cb_recipe_category = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Select category")
        self.cb_recipe_category.setObjectName("ComboBox")
        self.cb_recipe_category.setProperty("context", "recipe_form")

        # Dietary Preference
        self.lbl_dietary_preference = QLabel("Dietary Preference")
        self.cb_dietary_preference = ComboBox(list_items=DIETARY_PREFERENCES, placeholder="Select dietary preference")
        self.cb_dietary_preference.setObjectName("ComboBox")
        self.cb_dietary_preference.setProperty("context", "recipe_form")

        # add labels and widgets to the form layout - two column layout with labels above inputs
        # Row 0: Recipe Name (full width)
        self._layout.addWidget(self.lbl_recipe_name, 0, 0, 1, 2)
        self._layout.addWidget(self.le_recipe_name, 1, 0, 1, 2)

        # Row 2-3: Total Time (left) and Servings (right)
        self._layout.addWidget(self.lbl_time, 2, 0, 1, 1)
        self._layout.addWidget(self.lbl_servings, 2, 1, 1, 1)
        self._layout.addWidget(self.le_time, 3, 0, 1, 1)
        self._layout.addWidget(self.le_servings, 3, 1, 1, 1)

        # Row 4-5: Meal Type (left) and Category (right)
        self._layout.addWidget(self.lbl_meal_type, 4, 0, 1, 1)
        self._layout.addWidget(self.lbl_category, 4, 1, 1, 1)
        self._layout.addWidget(self.cb_meal_type, 5, 0, 1, 1)
        self._layout.addWidget(self.cb_recipe_category, 5, 1, 1, 1)

        # Row 6-7: Dietary Preference (left column only)
        self._layout.addWidget(self.lbl_dietary_preference, 6, 0, 1, 1)
        self._layout.addWidget(self.cb_dietary_preference, 7, 0, 1, 1)

        set_fixed_height_for_layout_widgets(
            layout = self._layout,
            height = FIXED_HEIGHT,
            skip   = (QLabel,)
        )
