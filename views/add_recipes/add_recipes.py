"""view/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QTextEdit, QVBoxLayout, QWidget)

from config import STYLES, UPLOAD_RECIPE_IMAGE
from config.config import INT_VALIDATOR, MEAL_CATEGORIES, NAME_VALIDATOR, RECIPE_CATEGORIES
from core.helpers import DebugLogger
from services.recipe_service import RecipeService
from style_manager import WidgetLoader
from ui.components.dialogs import MessageDialog
from ui.components.form_field import ComboBoxField, LineEditField
from ui.components.widget_frame import WidgetFrame
from ui.tools import clear_error_styles, dynamic_validation

from .ingredient_widget import IngredientWidget
from .upload_recipe import UploadRecipeImage
from services.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientInputDTO
from services.ingredient_service import IngredientService

# ── Class Definition ────────────────────────────────────────────────────────────
class AddRecipes(QWidget):
    """AddRecipes widget for creating new recipes with ingredients and directions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipes")
        WidgetLoader.apply_widget_style(self, STYLES["INGREDIENT_WIDGET"])

        self.ingredient_widgets = []
        self.stored_ingredients = []
        self.selected_image_path = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        # ── Main Layout ──
        # horizontal layout for main content. creates left and right sections
        self.lyt_main = QVBoxLayout(self) 
        self.lyt_main.setContentsMargins(20, 20, 20, 20)
        self.lyt_main.setSpacing(16)

        # ── Header Row ──
        self.header_layout = QHBoxLayout()

        # create header label
        self.lbl_header = QLabel("Recipe Details")
        self.lbl_header.setObjectName("HeaderLabel")

        # create save button
        self.btn_save = QPushButton("Save Recipe")
        self.btn_save.setObjectName("SaveButton")
        self.btn_save.setFixedSize(QSize(120, 40))

        # add widgets to header layout
        self.header_layout.addWidget(self.lbl_header, alignment=Qt.AlignLeft)
        self.header_layout.addWidget(self.btn_save, alignment=Qt.AlignRight)
        
        self.lyt_main.addLayout(self.header_layout)  # add header layout to lyt_main

        # ── Main Content ──
        self.lyt_main_content = QHBoxLayout()  # horizontal layout for left and right sections
        self.lyt_left_section = QVBoxLayout()  # left section for recipe details and ingredients
        self.lyt_left_section.setSpacing(16)

        # ── Recipe Details ──
        self.lyt_recipe_details = QHBoxLayout()  # layout for details & image/save buttons
        self.recipe_details = WidgetFrame(  # includes layout for recipe details
            header_text = "Recipe Details",
            layout_cls  = QGridLayout,  
            spacing     = 10,
        )
        
        # create form fields for recipe details
        self.le_recipe_name = LineEditField(
            label_text  = "Recipe Name:", 
            placeholder = "Enter recipe name here...",
        ) 
        self.cb_recipe_category = ComboBoxField(
            label_text = "Category:", 
            item_list  = RECIPE_CATEGORIES,
        )
        self.le_time = LineEditField(
            label_text = "Total Time:", 
            placeholder = "e.g. 30 mins...",
        ) 
        self.cb_meal_type = ComboBoxField(
            label_text = "Meal Type:", 
            item_list  = MEAL_CATEGORIES,
        )
        self.le_servings = LineEditField(
            label_text=  "Servings:", 
            placeholder="e.g. 4 servings...",
        ) 

        # add widgets to the recipe details frame
        self.recipe_details.addWidget(self.le_recipe_name, 0, 0, 1, 2)  # row 1
        self.recipe_details.addWidget(self.cb_recipe_category, 1, 0, 1, 1)  # row 2
        self.recipe_details.addWidget(self.le_time, 1, 1, 1, 1)
        self.recipe_details.addWidget(self.cb_meal_type, 2, 0, 1, 1)  # row 3
        self.recipe_details.addWidget(self.le_servings, 2, 1, 1, 1)

        self.lyt_recipe_details.addWidget(self.recipe_details)  # add details frame to details layout

        # ── Create Image & Save Buttons ──
        self.btn_upload_image = UploadRecipeImage()  # widget for uploading recipe image
        self.lyt_recipe_details.addWidget(self.btn_upload_image, alignment=Qt.AlignVCenter)
       
        self.lyt_left_section.addLayout(self.lyt_recipe_details)  # add recipe details to left section

        # ── Ingredients ──
        self.ingredients_frame = WidgetFrame(  # scrollable frame for ingredients
            header_text = "Ingredients",
            layout_cls = QVBoxLayout,
            scrollable  = True,
            spacing     = 0
        )
        self._add_ingredient(removable=False)  # add initial ingredient widget (not removable)
        self.lyt_left_section.addWidget(self.ingredients_frame, stretch=2)  # add ingredients frame to left section
        
        self.lyt_main_content.addLayout(self.lyt_left_section, 1)  # add left section to main content layout
        
        # ── Directions──
        self.directions_frame = WidgetFrame(  # frame for directions
            header_text = "Directions", 
            layout_cls  = QVBoxLayout,
        )
        self.te_directions = QTextEdit()  # text edit for directions
        self.te_directions.setObjectName("DirectionsTextEdit")
        self.te_directions.setPlaceholderText("Enter cooking directions here...")
        
        self.directions_frame.addWidget(self.te_directions, stretch=1)  # add text edit to directions frame

        self.lyt_main_content.addWidget(self.directions_frame, 2)  # add left section to main content layout

        self.lyt_main.addLayout(self.lyt_main_content)  # add main content layout to main layout

    def _connect_signals(self):
        self.btn_save.clicked.connect(self.save_recipe)
        self.btn_upload_image.image_uploaded.connect(self._update_image_path)
        
        dynamic_validation(self.le_recipe_name, NAME_VALIDATOR)
        dynamic_validation(self.le_servings, INT_VALIDATOR)
        
        self.cb_recipe_category.selection_validated.connect(lambda: clear_error_styles(self.cb_recipe_category))
        self.cb_meal_type.selection_validated.connect(lambda: clear_error_styles(self.cb_meal_type))
        self.te_directions.textChanged.connect(lambda: clear_error_styles(self.te_directions))

    def _add_ingredient(self, removable=True):
        widget = IngredientWidget(removable=removable)
        widget.remove_ingredient_requested.connect(self._remove_ingredient)
        widget.add_ingredient_requested.connect(self._add_ingredient)
        widget.ingredient_validated.connect(self._store_ingredient)
        self.ingredient_widgets.append(widget)
        self.ingredients_frame.addWidget(widget)

    def _remove_ingredient(self, widget):
        self.ingredients_frame.layout().removeWidget(widget)
        widget.deleteLater()
        self.ingredients_frame.update()

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
                RecipeIngredientInputDTO(
                    ingredient_name=data["ingredient_name"],
                    ingredient_category=data["ingredient_category"],
                    quantity=data["quantity"],
                    unit=data["unit"],
                )
                for data in raw_ingredients
            ]
        except Exception as dto_err:
            DebugLogger().log(f"[AddRecipes] DTO construction failed: {dto_err}", "error")
            MessageDialog(
                "warning",
                "Invalid Ingredient Data",
                "One of your ingredients has missing/invalid fields. Please double-check.",
                self
            ).exec()
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

        # ── create recipe with RecipeService ──
        try:
            new_recipe = RecipeService.create_recipe_with_ingredients(recipe_dto)
        except Exception as svc_err:
            DebugLogger().log(f"[AddRecipes.save_recipe] Error saving recipe: {svc_err}", "error")
            MessageDialog(
                "warning",
                "Failed to Save Recipe",
                f"Oops! Couldn’t save your recipe. 😢\n\nDetails: {svc_err}",
                self
            ).exec()
            return

        # ── success! ──
        DebugLogger().log(f"[AddRecipes] Recipe '{new_recipe.recipe_name}' saved with ID={new_recipe.id}", "info")
        MessageDialog(
            "info",
            "Success! 🎉",
            f"Your recipe '{new_recipe.recipe_name}' was saved successfully.",
            self
        ).exec()

        # ── clear form and reset state ──
        self._clear_form()            
        self.stored_ingredients.clear()
        for widget in self.ingredient_widgets:
            widget.deleteLater() # remove each IngredientWidget from the layout/UI
        self.ingredient_widgets = [] 

    def to_payload(self):
        """Collect all recipe form data and return it as a dict for API calls."""
        return {
            "recipe_name":     self.le_recipe_name.text().strip(),
            "recipe_category": self.cb_recipe_category.currentText().strip(),
            "meal_type":       self.cb_meal_type.currentText().strip(),
            "total_time":      int(self.le_time.text().strip() or 0),
            "servings":        int(self.le_servings.text().strip() or 0),
            "directions":      self.te_directions.toPlainText().strip(),
            "image_path":      self.selected_image_path or "",
        }

    def _clear_form(self):
        """Clear all form fields after successful save."""
        self.le_recipe_name.clear()
        self.cb_recipe_category.setCurrentIndex(-1)
        self.cb_meal_type.setCurrentIndex(-1)
        self.le_time.clear()
        self.le_servings.clear()
        self.te_directions.clear()
        self.btn_upload_image.clear_image()
        self.selected_image_path = None
        
        # Clear stored ingredients and widgets
        self.stored_ingredients.clear()
        for widget in self.ingredient_widgets:
            self.ingredients_frame.removeWidget(widget)
            widget.deleteLater()
        self.ingredient_widgets.clear()
        
        # Add back the initial ingredient widget
        self._add_ingredient(removable=False)
