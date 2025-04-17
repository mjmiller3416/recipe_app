# 🔸 Standard Library Imports
import os # Added for path joining

# 🔸 Third-party Imports
from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QSizePolicy,
    QDialog, QHBoxLayout, QPushButton, QVBoxLayout
)
from PySide6.QtGui import QPixmap, QMouseEvent,QIcon
from PySide6.QtCore import Signal, Qt, QSize, QTimer # Import QTimer

# 🔸 Local Imports
from core.modules.recipe_module import Recipe
from core.helpers.app_helpers import load_stylesheet
from core.helpers.ui_helpers import set_scaled_image
from core.helpers.debug_logger import DebugLogger
# Import the new layout builders
from .layouts._medium_layout import build_full_layout
from .layouts._small_layout import build_mini_layout
# Import constants from the new config file
from ._config import (
    FULL_CARD_WIDTH, FULL_IMAGE_HEIGHT,
    MINI_IMAGE_SIZE
)
from ._recipe_selection_dialog import RecipeSelectionDialog
from database import DB_INSTANCE
from core.helpers.config import icon_path


class RecipeWidget(QFrame):
    """
    A reusable card widget to preview recipe data.

    Supports two visual layout modes ("medium" and "small") and
    an optional meal selection mode that alters interaction behavior.

    Args:
        recipe (Recipe): The Recipe model instance to render.
        layout_mode (str): Layout variant, either "medium" or "small".
        is_meal_selection (bool): Whether this card is in meal selection context.
        parent (QWidget, optional): Parent widget for proper styling context.

    Attributes:
        recipe (Recipe): The Recipe model instance.
        recipe_id (int): The ID of the recipe.
        layout_mode (str): Current layout mode ("medium" or "small").
        is_meal_selection (bool): Flag for meal selection context.

    Raises:
        ValueError: If an invalid layout mode is provided.
    """

    # 🔹 Signals
    recipe_clicked = Signal(int)        # Emitted when card is clicked in default mode
    recipe_selected = Signal(object)    # Emitted when selected in meal planner mode (dict or (meal_type, id))

    def __init__(self, recipe=None, layout_mode="medium", meal_selection=False, parent=None, meal_type="main"):
        super().__init__(parent)

        self.meal_type = meal_type
        self.is_meal_selection = meal_selection
        self.recipe = recipe
        self.recipe_id = recipe.id if recipe else None
        self.layout_mode = layout_mode
        self._add_mode = recipe is None and meal_selection

        self.setObjectName("RecipeWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setProperty("layoutMode", self.layout_mode)

        load_stylesheet(self, "_stylesheet.qss")

        self._show_correct_state()

    # Use the simpler _clear_layout
    def _clear_layout(self):
        old_layout = self.layout()
        if old_layout is not None:
            # Dissociate the layout from this widget.
            self.setLayout(None)
            # Schedule the old layout and its contents for deletion.
            old_layout.deleteLater()

    # Remove the complex _clear_nested_layout helper
    # def _clear_nested_layout(self, layout_to_clear): ...

    # _show_correct_state already sets widget references to None first (from previous step)
    # _setup_add_meal_ui calls _clear_layout
    # build_ui calls _clear_layout

    def _show_correct_state(self):
        # Explicitly clear widget references BEFORE clearing layout/building UI
        self.lbl_image = None
        self.lbl_name = None
        self.lbl_servings_title = None
        self.servings_icon = None
        self.lbl_servings = None
        self.lbl_time_title = None
        self.lbl_time = None
        self.meta_container = None
        self.btn_add_meal = None # Also clear button reference

        # Now handle state logic which calls _clear_layout and build_ui
        if self.recipe is None and self.is_meal_selection:
            self._setup_add_meal_ui() # Calls _clear_layout
        elif self.recipe is not None:
            self.build_ui() # Calls _clear_layout, creates new widgets
            # Call populate directly now, as _show_correct_state is already deferred
            self.populate()
        else:
             self._clear_layout() # Ensure layout is cleared if no state applies

    def _setup_add_meal_ui(self):
        self._clear_layout()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.btn_add_meal = QPushButton()
        self.btn_add_meal.setObjectName("btn_add_meal")
        self.btn_add_meal.setStyleSheet("background: transparent;")
        self.btn_add_meal.setIcon(QIcon(icon_path("add_meal")))
        self.btn_add_meal.setIconSize(QSize(50, 50))
        self.btn_add_meal.clicked.connect(self.open_recipe_selection)
        layout.addWidget(self.btn_add_meal, alignment=Qt.AlignCenter)

    # In RecipeWidget class

    def open_recipe_selection(self):
        # Keep 'self' as parent for styling and ownership
        dialog = RecipeSelectionDialog(self)
        # --- Change Start ---
        # Connect the dialog's accepted signal to a handler slot
        # Note: Ensure only one connection if this method can be called multiple times
        try: dialog.accepted.disconnect(self._handle_recipe_selected) # Prevent duplicates
        except RuntimeError: pass # Ignore if not connected
        dialog.accepted.connect(self._handle_recipe_selected)

        # Use open() for non-blocking display instead of exec()
        dialog.open()
        # --- Change End ---

    # New slot to handle the selection AFTER the dialog is accepted
    def _handle_recipe_selected(self):
        # The sender() is the dialog that emitted the accepted signal
        dialog = self.sender()
        # Check if the sender is the correct dialog and has a selection
        if dialog and isinstance(dialog, RecipeSelectionDialog) and dialog.selected_recipe:
            # Call set_selected_recipe with the ID stored in the dialog
            # This runs safely after the dialog context is resolved
            self.set_selected_recipe(dialog.selected_recipe)

        # Optional: Explicitly schedule the dialog for deletion if needed,
        # though Qt's parent/child system should handle it if dialog's parent is self.
        # if dialog:
        #     dialog.deleteLater()

    # You might need to adjust where self.recipe_selected.emit() is called.
    # Currently, it's in set_selected_recipe. If you need it emitted *only*
    # after the user selects via the dialog, you could move it to the end
    # of _handle_recipe_selected.
    # def set_selected_recipe(self, recipe_id):
    #     # ... (existing code to fetch recipe, set self.recipe, etc.) ...
    #     self._show_correct_state()
    #     # Consider if self.recipe_selected.emit should be here or in the handler
    #     # self.recipe_selected.emit((self.meal_type, recipe_id)) # Maybe move this

    def set_selected_recipe(self, recipe_id):
        recipe = DB_INSTANCE.get_recipe(recipe_id)
        if not recipe:
            return
        # Ensure self.recipe is always a Recipe object
        if isinstance(recipe, dict):
            recipe = Recipe(recipe)
        self.recipe = recipe
        self.recipe_id = recipe_id
        self._add_mode = False
        # Schedule the UI update instead of calling _show_correct_state directly
        # QTimer.singleShot(0, self._update_ui_after_selection) # REMOVED
        self._show_correct_state() # CALL DIRECTLY
        self.recipe_selected.emit((self.meal_type, recipe_id))

    def clear(self):
        self.recipe = None
        self.recipe_id = None
        self._add_mode = True
        self._show_correct_state()

    def build_ui(self):
        self._clear_layout()
        # Build the new layout using imported functions
        if self.layout_mode == "small":
            new_layout = build_mini_layout(self) # Get the layout
        else: # Default to medium
            new_layout = build_full_layout(self) # Get the layout
        self.setLayout(new_layout) # Set the layout on the widget

    def populate(self):
        """Populates the UI based on the current layout mode."""
        if not self.recipe: return # Guard clause

        # Check if widgets exist before populating (important if build fails or called early)
        if self.layout_mode == "small":
            if self.lbl_name: self.lbl_name.setText(self.recipe.name)
            if self.lbl_image: self.set_image(self.recipe.image_path)
        elif self.layout_mode == "medium":
            if self.lbl_name: self.lbl_name.setText(self.recipe.name)
            if self.lbl_servings: self.lbl_servings.setText(self.recipe.formatted_servings())
            if self.lbl_time: self.lbl_time.setText(self.recipe.formatted_time())
            if self.lbl_image: self.set_image(self.recipe.image_path)
        else:
            # This case should ideally not be reached if __init__ validates
             try:
                 raise ValueError(f"Invalid layout mode '{self.layout_mode}'. Use 'medium' or 'small'.")
             except ValueError as e:
                  DebugLogger.exception(e) # Log the error

    def set_image(self, image_path):
        """
        Sets the image for the RecipeWidget based on the provided path.

        Args:
            image_path (str): The path to the recipe image file.
        """
        if not self.lbl_image: return # Check if image label exists

        if self.layout_mode == "small":
             # Use the imported constant directly
             size = MINI_IMAGE_SIZE
        else: # Default to medium size
             # Use the imported constants directly
             size = QSize(FULL_CARD_WIDTH, FULL_IMAGE_HEIGHT)

        set_scaled_image(self.lbl_image, image_path, size)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles clicks based on is_meal_selection flag:
        - If False (default), opens FullRecipe (TODO)
        - If True, emits recipe_selected (TODO)

        Args:
            event (QMouseEvent): Mouse click event
        """
        if self.is_meal_selection and self.recipe is not None:
            self.emit_selection()
        elif self.recipe is not None:
            self.show_full_recipe()

    def show_full_recipe(self):
        """
        Opens the FullRecipe dialog using the current recipe model.
        """
        DebugLogger.log("RecipeWidget clicked: Show full recipe for ID {self.recipe_id}", "info")
        # Import FullRecipe directly from _full_recipe
        from ._full_recipe import FullRecipe

        # Check if recipe data is loaded
        if self.recipe:
            # Pass the recipe ID to the dialog
            dialog = FullRecipe(self.recipe_id, self) # Pass recipe_id
            dialog.exec()
        else:
            DebugLogger.log("No recipe data available to show full recipe.", "warning")

        self.recipe_clicked.emit(self.recipe_id)

    def emit_selection(self):
        """
        Emits the recipe_selected signal to notify caller. (Placeholder)
        """
        if self.recipe:
            payload = {'id': self.recipe_id, 'name': self.recipe.name}
            self.recipe_selected.emit(payload)

    def set_meal_selection(self, enabled: bool):
        """
        Updates whether the card should behave in meal selection mode.

        Args:
            enabled (bool): Toggle meal selection logic
        """
        self.is_meal_selection = enabled
        self._show_correct_state()
