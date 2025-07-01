"""app/ui/pages/add_recipes/add_recipes.py

AddRecipes widget for creating new recipes with ingredients and directions.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QWidget)

from app.config.config import INT_VALIDATOR, NAME_VALIDATOR, THEME
from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientInputDTO
from app.core.services.recipe_service import RecipeService
from app.core.dev_tools import DebugLogger
from app.ui.components.dialogs import MessageDialog
from app.ui.components.forms  import RecipeForm
from app.ui.components.layout import WidgetFrame
from app.ui.helpers import clear_error_styles, dynamic_validation

from app.ui.components.forms import IngredientWidget
from app.ui.components.images.upload_recipe_image import UploadRecipeImage


# ── Class Definition ────────────────────────────────────────────────────────────
class AddRecipes(QWidget):
    """AddRecipes widget for creating new recipes with ingredients and directions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipes")

        DebugLogger.log("Initializing Add Recipes page", "debug")

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

        # create header label - used for feedback messages
        self.lbl_header = QLabel("")

        self.lbl_header.setObjectName("HeaderLabel")

        self.lyt_main.addWidget( # add header label to main layout
            self.lbl_header, 
            alignment=Qt.AlignLeft)  

        # ── Main Content ──
        self.lyt_main_content = QHBoxLayout()  # horizontal layout for left and right sections
        self.lyt_left_section = QVBoxLayout()  # left section for recipe details and ingredients
        self.lyt_left_section.setSpacing(16)

        # ── Recipe Details ──
        self.lyt_recipe_details = QHBoxLayout()
        self.lyt_recipe_details.setContentsMargins(0, 0, 0, 0)

        # recipe details form wrapped in a WidgetFrame
        self.recipe_details_frame = WidgetFrame(
            title="Recipe Details",
            layout=QVBoxLayout,
        )
        self.recipe_form = RecipeForm()  # custom form for recipe details
        self.recipe_details_frame.addWidget(self.recipe_form)

        # expose form fields for convenience
        self.le_recipe_name = self.recipe_form.le_recipe_name
        self.cb_recipe_category = self.recipe_form.cb_recipe_category
        self.le_time = self.recipe_form.le_time
        self.cb_meal_type = self.recipe_form.cb_meal_type
        self.le_servings = self.recipe_form.le_servings

        self.lyt_recipe_details.addWidget(
            self.recipe_details_frame)  # add recipe form frame to layout

        # ── Buttons ──
        self.lyt_buttons =QVBoxLayout()  # vertical layout for buttons

        # upload image button
        self.btn_upload_image = UploadRecipeImage() 
        self.btn_upload_image.setObjectName("UploadRecipeImage")
        self.lyt_buttons.addWidget(
            self.btn_upload_image)  # add upload image button to buttons layout

        # save button
        self.btn_save = QPushButton("Save Recipe")
        self.btn_save.setObjectName("SaveButton")
        self.btn_save.setFixedHeight(50)  # set fixed height for consistency
        self.lyt_buttons.addWidget(
            self.btn_save) # add save button to buttons layout

        self.lyt_recipe_details.addLayout(
            self.lyt_buttons)  # add buttons layout to recipe details layout
        self.lyt_left_section.addLayout(
            self.lyt_recipe_details)  # add recipe details layout to left section layout
        
        # ── Ingredients ──
        self.ingredients_frame = WidgetFrame(  # scrollable frame for ingredients
            title = "Ingredients",
            layout = QVBoxLayout,
            scrollable  = True,
            spacing     = 6
        )
        self._add_ingredient(removable=False)  # add initial ingredient widget 
        self.lyt_left_section.addWidget(
            self.ingredients_frame, stretch=2)  # add ingredients frame to left section
        self.lyt_main_content.addLayout(
            self.lyt_left_section, 1)  # add left section to main content layout
        
        # ── Directions──
        self.directions_frame = WidgetFrame(  # frame for directions
            title = "Directions", 
            layout  = QVBoxLayout,
        )
        self.te_directions = QTextEdit()  # text edit for directions
        self.te_directions.setObjectName("DirectionsTextEdit")
        self.te_directions.setPlaceholderText("Enter cooking directions here...")
        
        self.directions_frame.addWidget(
            self.te_directions, stretch=1)  # add text edit to directions frame
        self.lyt_main_content.addWidget(
            self.directions_frame, 2)  # add left section to main content layout
        self.lyt_main.addLayout(
            self.lyt_main_content)  # add main content layout to main layout

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
        """Remove the specified ingredient widget from the frame."""
        self.ingredients_frame.removeWidget(widget)
        widget.deleteLater()
        self.ingredients_frame.update()
        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)

    def _store_ingredient(self, data):
        self.stored_ingredients.append(data)

    def _update_image_path(self, image_path: str):
        """Update the selected image path when an image is selected."""
        self.selected_image_path = image_path if image_path else None

    def _display_save_message(self, message: str, success: bool = True):
        """Display save result message in the header label."""
        color = THEME["FONT"]["COLOR"]["SUCCESS"] if success else THEME["FONT"]["COLOR"]["ERROR"]
        self.lbl_header.setText(message)
        self.lbl_header.setStyleSheet(f"color: {color}; font-style: italic;")

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
            container = widget.parent()
            self.ingredients_frame.removeWidget(container)
            container.deleteLater()
        self.ingredient_widgets.clear()
        
        # Add back the initial ingredient widget
        self._add_ingredient(removable=False)
