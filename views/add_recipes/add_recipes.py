# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLineEdit, QTextEdit, QFrame
)

from config.config import INT, NAME, RECIPE_CATEGORIES
from core.helpers import DebugLogger
from services.recipe_service import RecipeService
from ui.components.dialogs import MessageDialog
from ui.components.inputs import CustomComboBox
from ui.tools import clear_error_styles, dynamic_validation
from ui.tools.form_utilities import populate_combobox
from .ingredient_widget import IngredientWidget
from .crop_image_dialog import CropImageDialog


# ── Class Definition ────────────────────────────────────────────────────────────
class AddRecipes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipes")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.ingredient_widgets = []
        self.stored_ingredients = []
        self.selected_image_path = None

        self._build_ui()
        self._connect_signals()
        #self._populate_categories()

    # ── UI Setup ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel("Recipe Details")
        btn_save = QPushButton("Save Recipe")
        btn_save.setObjectName("btn_save_recipes")
        self.btn_save = btn_save
        header.addWidget(lbl_title)
        header.addStretch()
        header.addWidget(btn_save)
        layout.addLayout(header)

        # Recipe Fields
        fields = QHBoxLayout()

        self.le_name = QLineEdit()
        self.le_name.setPlaceholderText("Enter recipe name")
        self.cb_category = CustomComboBox(list=RECIPE_CATEGORIES, placeholder="Meal Type")
        self.cb_category.setPlaceholderText("Meal Type")
        self.le_time = QLineEdit()
        self.le_time.setPlaceholderText("e.g., 45")
        self.le_servings = QLineEdit()
        self.le_servings.setPlaceholderText("e.g., 4")
        self.btn_image = QPushButton("Browse")
        self.btn_image.setMaximumWidth(75)
        self.btn_image.setObjectName("btn_image_path")

        fields.addWidget(QLabel("Recipe Name:"))
        fields.addWidget(self.le_name)
        fields.addWidget(QLabel("Category:"))
        fields.addWidget(self.cb_category)
        fields.addWidget(QLabel("Total Time:"))
        fields.addWidget(self.le_time)
        fields.addWidget(QLabel("Servings:"))
        fields.addWidget(self.le_servings)
        fields.addWidget(QLabel("Image Path:"))
        fields.addWidget(self.btn_image)
        layout.addLayout(fields)

        # Ingredient Section
        layout.addWidget(QLabel("Ingredients:"))
        scroll = QScrollArea()
        scroll.setContentsMargins(0, 0, 0, 0)
        scroll.setWidgetResizable(True)
        self.ingredients_container = QWidget()
        self.ingredients_container.setObjectName("ingredients_container")
        self.ingredients_layout = QVBoxLayout(self.ingredients_container)
        self.ingredients_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.ingredients_container)
        layout.addWidget(scroll)

        # First Ingredient (non-removable)
        self._add_ingredient(removable=False)

        # Directions
        layout.addWidget(QLabel("Directions:"))
        self.te_directions = QTextEdit()
        layout.addWidget(self.te_directions)

    # ── Signal Connections ───────────────────────────────────────────────────────
    def _connect_signals(self):
        self.btn_save.clicked.connect(self.save_recipe)
        self.btn_image.clicked.connect(self.select_image)

        dynamic_validation(self.le_name, NAME)
        dynamic_validation(self.le_servings, INT)
        dynamic_validation(self.le_time, INT)

        self.cb_category.cb_validated.connect(lambda: clear_error_styles(self.cb_category))
        self.te_directions.textChanged.connect(lambda: clear_error_styles(self.te_directions))

    # ── Combobox Setup ───────────────────────────────────────────────────────────
    def _populate_categories(self):
        populate_combobox(self.cb_category, *RECIPE_CATEGORIES)

    # ── Ingredient Management ────────────────────────────────────────────────────
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

    # ── Image Picker ────────────────────────────────────────────────────────────
    def select_image(self):
        dialog = CropImageDialog(self)
        if dialog.exec():
            self.selected_image_path = dialog.get_image_path()
            if self.selected_image_path:
                self.btn_image.setText("Image Selected")

    # ── Save Logic ──────────────────────────────────────────────────────────────
    def save_recipe(self):
        recipe_data = {
            "recipe_name": self.le_name.text().strip(),
            "recipe_category": self.cb_category.currentText().strip(),
            "total_time": int(self.le_time.text().strip() or 0),
            "servings": int(self.le_servings.text().strip() or 0),
            "directions": self.te_directions.toPlainText().strip(),
            "image_path": self.selected_image_path or ""
        }

        # Call service
        try:
            recipe = RecipeService.create_recipe_with_ingredients(
                recipe_data,
                self.stored_ingredients
            )
            MessageDialog("info", "Success!", "Recipe saved successfully.", self).exec()
        except Exception as e:
            DebugLogger().log(f"[AddRecipes] Error saving recipe: {e}", "error")
            MessageDialog("warning", "Failed to Save", str(e), self).exec()
