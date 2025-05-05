# Package: app.add_recipes

# Description: This file contains the AddRecipes class, which is a custom widget that represents the Add Recipe screen. It allows
# users to input recipe details such as name, category, ingredients, total time, and servings. The AddRecipes class communicates
# with the ApplicationDatabase class to save the recipe data to the database. It also uses the IngredientWidget class to manage the
# input of individual ingredients.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from config.config import INT, NAME, RECIPE_CATEGORIES
from core.helpers import DebugLogger
from ui.components.dialogs import MessageDialog
from ui.tools import clear_error_styles, dynamic_validation
from ui.tools.form_utilities import populate_combobox

from .crop_image_dialog import CropImageDialog
from .ingredient_widget import IngredientWidget
#🔸Local Imports
from .ui_add_recipes import Ui_AddRecipes


class AddRecipes(QWidget):
    """Subclass of the generated UI for the Add Recipe screen."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize & Setup UI
        self.ui = Ui_AddRecipes()
        self.ui.setupUi(self)
        self.setObjectName("AddRecipes")

        # Initialize ingredient widgets and stored ingredients list
        self.ingredient_widgets = []  # List to store ingredient widgets
        self.stored_ingredients = []  # List to store ingredient data

        # Set up widgets
        self.setup_widgets()

        # Populate comboboxes
        self.populate_combobox()

        # Connect signals and slots
        self.setup_event_logic()

        # Store the selected image path
        self.selected_image_path = None

    @property
    def recipe_data(self):
        """Returns the current ingredient data as a dictionary."""

        return {
            "le_recipe_name": self.ui.le_recipe_name,
            "cb_recipe_category": self.ui.cb_recipie_category,
            "le_total_time": self.ui.le_total_time,
            "le_servings": self.ui.le_servings,
            "te_directions": self.ui.te_directions,
            "image_path": self.selected_image_path
        }

    def setup_event_logic(self):
        """Connects the signals and slots for the Add Recipe screen."""

        # Connect save button to save_recipe method
        self.ui.btn_save_recipes.clicked.connect(self.save_recipe)

        # Dynamic validation for QLineEdit fields
        dynamic_validation(self.ui.le_recipe_name, NAME)
        dynamic_validation(self.ui.le_servings, INT)
        dynamic_validation(self.ui.le_total_time, INT)

        # Dynamic (positive) validation for recipe category
        self.ui.cb_recipie_category.cb_validated.connect(
            lambda:clear_error_styles(self.ui.cb_recipie_category)
        )

        # Dynamic (positive) validation for directions
        self.ui.te_directions.textChanged.connect(
            lambda:clear_error_styles(self.ui.te_directions)
        )

        # Ensure there is at least one ingredient
        if self.ingredient_widgets:
            first_ingredient: IngredientWidget = self.ingredient_widgets[0]  # Get the first widget

            # Connect signals for the first ingredient
            first_ingredient.remove_ingredient_requested.connect(self.remove_ingredient)
            first_ingredient.add_ingredient_requested.connect(self.add_new_ingredient)
            first_ingredient.ingredient_validated.connect(self.receive_ingredient_data)

        # Connect Browse button for image selection
        self.ui.btn_image_path.clicked.connect(self.select_image)

    def save_recipe(self):
        """
        Validates and formats recipe data, saves the recipe, then saves all ingredients.
        """

        # 1️⃣: Collect raw widget data
        recipe_fields = self.recipe_data

        # 2️⃣: Validate recipe data
        #if validate_data_fields(recipe_fields):
            #DebugLogger().log("🔵 Recipe Validation Passed", "info")

            # 3️⃣: Format recipe data
            #formatted_data = format_recipe_data(**recipe_fields)
            #DebugLogger().log("🟢 Recipe Formatted: {formatted_data}\n", "debug")

            # 4️⃣: Insert recipe, get its new ID
            #recipe_id = ApplicationDatabase().save_recipe(formatted_data)
            #if recipe_id:
                # 5️⃣: Save all ingredients for this recipe
                #self.save_ingredients(recipe_id)
                #DebugLogger().log("🟢 Recipe Saved Successfully with ID: {recipe_id}", "debug")

                # Show success message
                #MessageDialog(
                    #message_type="info",
                    #message="Success!",
                    #description="Your recipe has been saved!",
                    #parent=self
                #).exec()
        #else:
            #DebugLogger().log("🔴 Recipe Validation Failed", "error")

    def save_ingredients(self, recipe_id):
        """
        Saves the ingredients to the database,
        linking each ingredient to the specified recipe_id.
        """
        DebugLogger().log("🔵 Saving Ingredients...", "info")
        # ApplicationDatabase().save_ingredients(recipe_id, self.stored_ingredients) ⚠️

    def add_new_ingredient(self, ingredient_widget):
        """Adds a new ingredient widget to the layout."""

        new_widget = IngredientWidget(removable=True)  # Create a new widget

        # Enable the subtract button for all newly added ingredients
        new_widget.ui.btn_subtract.setEnabled(True)

        # Store the new widget in the list
        self.ingredient_widgets.append(new_widget)

        # Connect signals for the new widget
        new_widget.remove_ingredient_requested.connect(self.remove_ingredient)
        new_widget.add_ingredient_requested.connect(self.add_new_ingredient)
        new_widget.ingredient_validated.connect(self.receive_ingredient_data)

        # Add new widget to layout
        self.sa_lyt.addWidget(new_widget)

        """ # Reapply hover effects since it's now enabled ⚠️
        StyleManager.apply_hover_effects(
            [new_widget.ui.btn_add, new_widget.ui.btn_subtract], (12, 12)
        ) """

    def remove_ingredient(self, ingredient_widget):
        """Removes an ingredient widget from the layout."""

        self.sa_lyt.removeWidget(ingredient_widget)
        ingredient_widget.deleteLater()
        self.sa_lyt.update()

    def receive_ingredient_data(self, ingredient_data):
        """Handles the updated ingredient data."""

        DebugLogger().log("🔵 Ingredient Data Received 🔵", "info")
        self.stored_ingredients.append(ingredient_data)  # Store the ingredient data
        DebugLogger().log("🟢 Ingredient Data Stored: {self.stored_ingredients}\n", "debug")

    def select_image(self):
        """Opens the CropImageDialog and stores the selected image path."""
        dialog = CropImageDialog(self)  # Create the dialog
        if dialog.exec():  # Execute it modally
            self.selected_image_path = dialog.get_image_path()  # Get the selected path
            if self.selected_image_path:
                self.ui.btn_image_path.setText("Image Selected")  # Update button text

    def setup_widgets(self):
        """Sets up the widgets for the Add Recipe screen and connects signals."""

        # Add layout for the ingredient widget
        self.sa_lyt = QVBoxLayout(self.ui.ingredients_container)  # Get the placeholder widget
        self.sa_lyt.setAlignment(Qt.AlignTop)  # Align to the top

        # Create the first ingredient widget with remove button disabled
        self.first_ingredient = IngredientWidget(removable=False)

        # Add the first ingredient widget to the layout
        self.sa_lyt.addWidget(self.first_ingredient)

        # Add the first ingredient widget to the list
        self.ingredient_widgets.append(self.first_ingredient)

    def populate_combobox(self):
        """Populates recipe category and unit comboboxes."""

        # Set up comboboxes
        populate_combobox(self.ui.cb_recipie_category, *RECIPE_CATEGORIES)

#🔸END
