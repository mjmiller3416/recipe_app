"""app/ui/components/forms/add_recipe_form.py

A form for adding new recipes, including fields for recipe details and an image 
upload button. 
"""

# ── Constants ───────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 60  # fixed height for input fields in the recipe form

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QWidget, QLabel

from app.ui.components.forms.form_field import LineEditField, ComboBoxField
from app.ui.components.layout.widget_frame import WidgetFrame
from app.ui.helpers.ui_helpers import set_fixed_height_for_layout_widgets

from app.config import RECIPE_CATEGORIES, MEAL_CATEGORIES

# ── Class Definition ────────────────────────────────────────────────────────────
class RecipeForm(WidgetFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            title   = "Recipe Details", 
            layout  = QGridLayout, 
            spacing = 10,
            parent  = parent, 
        )
        self.setObjectName("WidgetFrame") # for styling purposes

        # create form fields for recipe details
        self.le_recipe_name = LineEditField(
            label_text  = "Recipe Name:", 
            placeholder = "Enter recipe name here...",
        ) 
        self.cb_recipe_category = ComboBoxField(
            label_text = "Category:", 
            placeholder = "Select a category...",
            item_list  = RECIPE_CATEGORIES,
        )
        self.le_time = LineEditField(
            label_text = "Total Time:", 
            placeholder = "e.g. 30 mins...",
        ) 
        self.cb_meal_type = ComboBoxField(
            label_text = "Meal Type:", 
            placeholder = "Select a meal type...",
            item_list  = MEAL_CATEGORIES,
        )
        self.le_servings = LineEditField(
            label_text=  "Servings:", 
            placeholder="e.g. 4 servings...",
        ) 

        # add widgets to the recipe details frame
        self.addWidget(self.le_recipe_name, 0, 0, 1, 2)  # row 1
        self.addWidget(self.cb_recipe_category, 1, 0, 1, 1)  # row 2
        self.addWidget(self.le_time, 1, 1, 1, 1)
        self.addWidget(self.cb_meal_type, 2, 0, 1, 1)  # row 3
        self.addWidget(self.le_servings, 2, 1, 1, 1)

        set_fixed_height_for_layout_widgets(
            layout = self.getLayout(), 
            height = FIXED_HEIGHT, 
            skip   = (QLabel)
        )
