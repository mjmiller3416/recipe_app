# 🔸 Standard Library Imports
import os # Added for path joining

# 🔸 Third-party Imports
from PySide6.QtWidgets import (
    QFrame, QWidget, QLabel, QVBoxLayout, QGridLayout, QSizePolicy,
    QSpacerItem, QDialog, QScrollArea, QTextEdit, QHBoxLayout, QLayout
)
from PySide6.QtGui import QPixmap, QMouseEvent, QFont
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

# 🔸 Local Imports
from core.modules.recipe_module import Recipe
from core.helpers.ui_helpers import set_scaled_image
from core.helpers import svg_loader # wrap_layout might not be needed here anymore
from core.helpers.config import icon_path, ICON_COLOR, ICON_SIZE
from core.helpers.debug_logger import DebugLogger
# Import the new layout builders
from .layouts._medium_layout import build_full_layout
from .layouts._small_layout import build_mini_layout


class RecipeWidget(QFrame):
    """
    A reusable card widget to preview recipe data.

    Supports two visual layout modes ("full" and "mini") and
    an optional meal selection mode that alters interaction behavior.

    Args:
        recipe (Recipe): The Recipe model instance to render.
        layout_mode (str): Layout variant, either "full" or "mini".
        is_meal_selection (bool): Whether this card is in meal selection context.
        parent (QWidget, optional): Parent widget for proper styling context.

    Attributes:
        recipe (Recipe): The Recipe model instance.
        recipe_id (int): The ID of the recipe.
        layout_mode (str): Current layout mode ("full" or "mini").
        is_meal_selection (bool): Flag for meal selection context.

    Raises:
        ValueError: If an invalid layout mode is provided.
    """

    # 🔹 Constants
    FULL_CARD_WIDTH = 280
    FULL_CARD_HEIGHT = 420
    FULL_IMAGE_HEIGHT = 280
    MINI_CARD_WIDTH = 280
    MINI_CARD_HEIGHT = 100 # Example, adjust as needed
    MINI_IMAGE_SIZE = QSize(100, 100) # Example, adjust as needed

    # Define spacing/margins constants
    FULL_LAYOUT_SPACING = 8           # Spacing between image/title/meta
    FULL_LAYOUT_MARGIN_LEFT = 12      # Increased horizontal padding
    FULL_LAYOUT_MARGIN_TOP = 0        # Image flush top
    FULL_LAYOUT_MARGIN_RIGHT = 12     # Increased horizontal padding
    FULL_LAYOUT_MARGIN_BOTTOM = 4     # Space below meta row
    META_LAYOUT_SPACING = 0           # Spacing within meta row (handled by stretch)
    META_LAYOUT_MARGIN_LEFT = 16      # Increased horizontal padding
    META_LAYOUT_MARGIN_TOP = 0        # Image flush top
    META_LAYOUT_MARGIN_RIGHT = 16     # Increased horizontal padding
    META_LAYOUT_MARGIN_BOTTOM = 8     # Increased bottom padding
    SERVINGS_TIME_LAYOUT_SPACING = 2  # Spacing within servings/time blocks
    SERVINGS_VALUE_ROW_SPACING = 4    # Spacing between icon and text
    MINI_LAYOUT_SPACING = 8           # Space between image and title
    MINI_LAYOUT_MARGIN_LEFT = 0       # Image flush left
    MINI_LAYOUT_MARGIN_TOP = 4        # Space above/below content
    MINI_LAYOUT_MARGIN_RIGHT = 0      # Image flush right
    MINI_LAYOUT_MARGIN_BOTTOM = 4     # Space above/below content

    # 🔹 Signals
    recipe_clicked = Signal(int)      # Emitted when card is clicked in default mode
    recipe_selected = Signal(dict)    # Emitted when selected in meal planner mode

    def __init__(self, recipe: Recipe, layout_mode="full", meal_selection=False, parent=None):
        super().__init__(parent)

        # 🔹 Store state and recipe info
        self.recipe = recipe
        self.recipe_id = recipe.id
        self.layout_mode = layout_mode            # "full" or "mini"
        self.is_meal_selection = meal_selection   # Toggle between selection and display

        # 🔹 Setup styling
        self.setObjectName("RecipeWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setProperty("layoutMode", self.layout_mode) # For QSS selector

        # 🔹 Load and apply stylesheet (Corrected Path)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Assuming the QSS file is named _style_sheet.qss as per the file structure
        stylesheet_path = os.path.join(script_dir, "_style_sheet.qss")
        try:
            with open(stylesheet_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            DebugLogger.log(f"Stylesheet not found: {stylesheet_path}", "warning")
        except Exception as e:
            DebugLogger.log_and_raise(f"Error loading stylesheet: {e}")

        # 🔹 Build and populate UI
        # References to widgets will be created in build methods
        self.lbl_image = None
        self.lbl_name = None
        self.lbl_servings_title = None
        self.servings_icon = None
        self.lbl_servings = None
        self.lbl_time_title = None
        self.lbl_time = None
        self.meta_container = None # Keep track if needed elsewhere

        self.build_ui()
        self.populate()

    def build_ui(self):
        """
        Constructs the appropriate UI layout based on layout_mode.
        Routes layout setup to the correct external function.
        Clears previous layout if any exists.
        """
        # Clear existing widgets and layout if rebuilding
        if self.layout() is not None:
            # Keep existing layout clearing logic
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    layout_item = item.layout()
                    if layout_item is not None:
                        while layout_item.count():
                             sub_item = layout_item.takeAt(0)
                             sub_widget = sub_item.widget()
                             if sub_widget:
                                 sub_widget.deleteLater()
                        layout_item.deleteLater()


        # Build the new layout using imported functions
        if self.layout_mode == "mini":
            build_mini_layout(self) # Pass self to the function
        else: # Default to full
            build_full_layout(self) # Pass self to the function

    def populate(self):
        """Populates the UI based on the current layout mode."""
        if not self.recipe: return # Guard clause

        # Check if widgets exist before populating (important if build fails or called early)
        if self.layout_mode == "mini":
            if self.lbl_name: self.lbl_name.setText(self.recipe.name)
            if self.lbl_image: self.set_image(self.recipe.image_path)
        elif self.layout_mode == "full":
            if self.lbl_name: self.lbl_name.setText(self.recipe.name)
            if self.lbl_servings: self.lbl_servings.setText(self.recipe.formatted_servings())
            if self.lbl_time: self.lbl_time.setText(self.recipe.formatted_time())
            if self.lbl_image: self.set_image(self.recipe.image_path)
        else:
            # This case should ideally not be reached if __init__ validates
             try:
                 raise ValueError(f"Invalid layout mode '{self.layout_mode}'. Use 'full' or 'mini'.")
             except ValueError as e:
                  DebugLogger.exception(e) # Log the error

    def set_image(self, image_path):
        """
        Sets the image for the RecipeWidget based on the provided path.

        Args:
            image_path (str): The path to the recipe image file.
        """
        if not self.lbl_image: return # Check if image label exists

        if self.layout_mode == "mini":
             size = self.MINI_IMAGE_SIZE
        else: # Default to full size
             size = QSize(self.FULL_CARD_WIDTH, self.FULL_IMAGE_HEIGHT)

        set_scaled_image(self.lbl_image, image_path, size)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles clicks based on is_meal_selection flag:
        - If False (default), opens FullRecipe (TODO)
        - If True, emits recipe_selected (TODO)

        Args:
            event (QMouseEvent): Mouse click event
        """
        if self.is_meal_selection:
             self.emit_selection()
        else:
             # Check if the click is within the image or title area perhaps?
             # For now, assume any click triggers showing full recipe
             self.show_full_recipe()
        # super().mousePressEvent(event) # Call super if needed for other interactions

    def show_full_recipe(self):
        """
        Opens the FullRecipe dialog using the current recipe model. (Placeholder)
        """
        DebugLogger.debug(f"RecipeWidget clicked: Show full recipe for ID {self.recipe_id}")
        # Import FullRecipe locally to avoid circular dependency if FullRecipe imports RecipeWidget
        try:
            # Adjust import path based on where FullRecipe is actually located
            # Assuming it's moved out of recipe_widget directory
            from features.view_recipes.full_recipe import FullRecipe # Example path
        except ImportError:
             # Fallback or alternative path if needed
             # Maybe it's still in recipe_widget?
             try:
                 from ._full_recipe import FullRecipe
             except ImportError as e:
                 DebugLogger.exception(f"Could not import FullRecipe: {e}")
                 return # Cannot proceed without FullRecipe class

        # Check if recipe data is loaded
        if self.recipe:
            # Pass the recipe ID to the dialog
            dialog = FullRecipe(self.recipe_id, self) # Pass recipe_id
            dialog.exec()
        else:
            DebugLogger.warning("No recipe data available to show full recipe.")

        self.recipe_clicked.emit(self.recipe_id)

    def emit_selection(self):
        """
        Emits the recipe_selected signal to notify caller. (Placeholder)
        """
        DebugLogger.debug(f"RecipeWidget selected for meal plan: {self.recipe.name} (ID: {self.recipe_id})")
        # Create dict payload, e.g., {'id': self.recipe_id, 'name': self.recipe.name}
        payload = {'id': self.recipe_id, 'name': self.recipe.name}
        self.recipe_selected.emit(payload)
        # TODO: Add visual feedback for selection?

    def set_meal_selection(self, enabled: bool):
        """
        Updates whether the card should behave in meal selection mode.

        Args:
            enabled (bool): Toggle meal selection logic
        """
        self.is_meal_selection = enabled
        # TODO: Optionally change visual style when in selection mode?
        # Example: self.setProperty("isSelecting", enabled); self.style().polish(self)