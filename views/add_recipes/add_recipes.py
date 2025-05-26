"""view/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QFrame, QScrollArea, QSizePolicy
)

from config.config import INT, NAME, RECIPE_CATEGORIES, MEAL_CATEGORIES
from core.helpers import DebugLogger
from services.recipe_service import RecipeService
from ui.components.dialogs import MessageDialog
from ui.components.inputs import SmartComboBox
from ui.tools import clear_error_styles, dynamic_validation
from ui.components.widget_frame import WidgetFrame
from .ingredient_widget import IngredientWidget

# ── Class Definition ────────────────────────────────────────────────────────────
class AddRecipes(QWidget):
    """AddRecipes widget for creating new recipes with ingredients and directions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipes")

        self.ingredient_widgets = []
        self.stored_ingredients = []
        self.selected_image_path = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        # ── Main Layout ──
        self.lyt_main = QVBoxLayout(self)
        self.lyt_main.setContentsMargins(20, 20, 20, 20)
        self.lyt_main.setSpacing(16)

        # ── Header Row ──
        header_layout = QHBoxLayout()
        self.lbl_header = QLabel("Recipe Details")
        self.lbl_header.setObjectName("header_label")
        header_layout.addWidget(self.lbl_header, alignment=Qt.AlignLeft)

        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("btn_save_recipes")
        header_layout.addWidget(self.btn_save, alignment=Qt.AlignRight)
        self.lyt_main.addLayout(header_layout)

        # ── Main Content ──
        main_content_layout = QHBoxLayout()
        main_content_layout.setSpacing(16)

        # ── Left Section (Inputs + Ingredients) ──
        lyt_recipe_details = QVBoxLayout()
        lyt_recipe_details.setSpacing(12)

       # ── Create vertical layout container ──
        input_vbox = QVBoxLayout()
        input_vbox.setSpacing(12)

        # ── Name Row ──
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(10)
        name_layout.addWidget(QLabel("Name:"))
        self.le_name = QLineEdit()
        name_layout.addWidget(self.le_name)
        input_vbox.addWidget(name_widget)

        # ── Category & Type Row ──
        category_widget = QWidget()
        category_layout = QHBoxLayout(category_widget)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(10)

        # Category label + combo
        category_label = QLabel("Category:")
        category_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        category_layout.addWidget(category_label)

        self.cb_recipe_category = SmartComboBox(list=RECIPE_CATEGORIES)
        category_layout.addWidget(self.cb_recipe_category, stretch=1)

        # Type label + combo
        type_label = QLabel("Type:")
        type_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        category_layout.addWidget(type_label)

        self.cb_meal_type = SmartComboBox(list=MEAL_CATEGORIES)
        category_layout.addWidget(self.cb_meal_type, stretch=1)

        input_vbox.addWidget(category_widget)


        # ── Total Time & Servings Row ──
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(10)
        time_layout.addWidget(QLabel("Total Time:"))
        self.le_time = QLineEdit()
        time_layout.addWidget(self.le_time)
        time_layout.addWidget(QLabel("Servings:"))
        self.le_servings = QLineEdit()
        time_layout.addWidget(self.le_servings)
        input_vbox.addWidget(time_widget)

        # ── Wrap Inputs + Image ──
        top_hbox = QHBoxLayout()
        top_hbox.setSpacing(20)
        top_hbox.addLayout(input_vbox, stretch=2)

        self.btn_add_image = QPushButton("+\nAdd Image")
        self.btn_add_image.setFixedSize(180, 180)
        top_hbox.addWidget(self.btn_add_image, alignment=Qt.AlignTop)

        lyt_recipe_details.addLayout(top_hbox)


        # Ingredients Section
        ingredients_frame = QFrame()
        ingredients_frame.setObjectName("ingredients_frame")
        ingredients_frame.setFrameShape(QFrame.Box)
        ingredients_layout = QVBoxLayout(ingredients_frame)
        ingredients_layout.setSpacing(20)
        ingredients_layout.addWidget(QLabel("Ingredients"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.ingredients_container = QWidget()
        self.ingredients_container.setObjectName("ingredients_container")
        self.ingredients_layout = QVBoxLayout(self.ingredients_container)
        self.ingredients_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.ingredients_container)
        ingredients_layout.addWidget(scroll)

        lyt_recipe_details.addWidget(ingredients_frame)

        main_content_layout.addLayout(lyt_recipe_details, 2)  # ~2/3 width

        # ── Directions──
        directions_frame = WidgetFrame( # frame for directions
            header_text = "Directions", 
            layout_type = "vertical"
        )
        self.te_directions = QTextEdit() # text edit for directions
        self.te_directions.setPlaceholderText("Enter cooking directions here...")
        self.te_directions.setObjectName("DirectionsTextEdit")
        directions_frame.add_widget(self.te_directions, stretch=1)
        main_content_layout.addWidget(directions_frame, 1) # add directions frame to main content

        self.lyt_main.addLayout(main_content_layout)

        # ── Initial Ingredient Slot ──
        self._add_ingredient(removable=False)

    def _connect_signals(self):
        self.btn_save.clicked.connect(self.save_recipe)
        #self.btn_add_image.image_selected.connect(self._update_image_path)
        
        dynamic_validation(self.le_name, NAME)
        dynamic_validation(self.le_servings, INT)
        
        self.cb_recipe_category.selection_validated.connect(lambda: clear_error_styles(self.cb_recipe_category))
        self.cb_meal_type.selection_validated.connect(lambda: clear_error_styles(self.cb_meal_type))
        self.te_directions.textChanged.connect(lambda: clear_error_styles(self.te_directions))

    def _add_ingredient(self, removable=True):
        widget = IngredientWidget(removable=removable)
        widget.remove_ingredient_requested.connect(self._remove_ingredient)
        widget.add_ingredient_requested.connect(self._add_ingredient)
        widget.ingredient_validated.connect(self._store_ingredient)
        self.ingredient_widgets.append(widget)
        self.ingredients_layout.addWidget(widget)

    def _remove_ingredient(self, widget):
        self.ingredients_layout.removeWidget(widget)
        widget.deleteLater()
        self.ingredients_layout.update()

    def _store_ingredient(self, data):
        self.stored_ingredients.append(data)

    def _update_image_path(self, image_path: str):
        """Update the selected image path when an image is selected."""
        self.selected_image_path = image_path if image_path else None

    def save_recipe(self):
        recipe_data = {
            "recipe_name": self.le_name.text().strip(),
            "recipe_category": self.cb_recipe_category.currentText().strip(),
            "meal_type": self.cb_meal_type.currentText().strip(),
            "total_time": int(self.le_time.text().strip() or 0),
            "servings": int(self.le_servings.text().strip() or 0),
            "directions": self.te_directions.toPlainText().strip(),
            "image_path": self.selected_image_path or ""
        }

        try:
            recipe = RecipeService.create_recipe_with_ingredients(
                recipe_data,
                self.stored_ingredients
            )
            MessageDialog("info", "Success!", "Recipe saved successfully.", self).exec()
            self._clear_form()  # Clear the form after successful save
        except Exception as e:
            DebugLogger().log(f"[AddRecipes] Error saving recipe: {e}", "error")
            MessageDialog("warning", "Failed to Save", str(e), self).exec()

    def _clear_form(self):
        """Clear all form fields after successful save."""
        self.le_name.clear()
        self.cb_recipe_category.setCurrentIndex(-1)
        self.cb_meal_type.setCurrentIndex(-1)
        self.le_time.clear()
        self.le_servings.clear()
        self.te_directions.clear()
        self.btn_add_image.clear_image()
        self.selected_image_path = None
        
        # Clear stored ingredients and widgets
        self.stored_ingredients.clear()
        for widget in self.ingredient_widgets:
            self.ingredients_layout.removeWidget(widget)
            widget.deleteLater()
        self.ingredient_widgets.clear()
        
        # Add back the initial ingredient widget
        self._add_ingredient(removable=False)
