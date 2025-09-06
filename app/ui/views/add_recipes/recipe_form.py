"""app/ui/views/add_recipes/recipe_form.py

Recipe form for entering basic recipe details like name, time, servings, meal type, category, and dietary
preference.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QWidget

from app.config import DIETARY_PREFERENCES, MEAL_TYPE, RECIPE_CATEGORIES
from app.ui.utils.layout_utils import create_labeled_form_grid

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
