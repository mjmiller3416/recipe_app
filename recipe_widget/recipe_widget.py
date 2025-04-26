# 🔸 Standard Library Imports
import os
from typing import Literal, Optional

# 🔸 Third-party Imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QStackedLayout, QWidget

from core.helpers.app_helpers import load_and_apply_stylesheet
# 🔸 Local Application Imports
from core.helpers.debug_logger import DebugLogger
from core.modules.recipe_module import Recipe
from database import DB_INSTANCE

from .config import (MEDIUM_CARD_HEIGHT, MEDIUM_CARD_WIDTH, SMALL_CARD_HEIGHT,
                     SMALL_CARD_WIDTH)
from .frame_layouts.build_empty_frame import build_empty_frame
from .frame_layouts.build_medium_frame import build_medium_frame
from .frame_layouts.build_small_frame import build_small_frame
from .full_recipe import FullRecipe
from .recipe_selection_dialog import RecipeSelectionDialog


class RecipeWidget(QFrame):
    """
    A container widget that displays a recipe card or an 'add' button.
    It manages switching between an empty state and different recipe display formats (medium, small)
    using a QStackedLayout.

    Properties:
        layoutMode (str): Controls the display format ('medium' or 'small').
        selection (bool): Indicates if the widget is in selection mode (not currently used for display logic).

    Signals:
        recipe_selected (Signal): Emitted when a recipe is chosen via the dialog (int: recipe_id).
        recipe_cleared (Signal): Emitted when the recipe is cleared (e.g., future feature).
        widget_clicked (Signal): Emitted when the populated widget (not the empty button) is clicked (int: recipe_id).
    """
    recipe_selected = Signal(int)
    recipe_cleared = Signal()
    widget_clicked = Signal(int) # Emitted when the frame itself is clicked

    def __init__(self,
                 parent: Optional[QWidget] = None,
                 recipe_id: Optional[int] = None,
                 layout_mode: Literal["medium", "small"] = "medium",
                 selection: bool = False):
        """
        Initialize the RecipeWidget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            recipe_id (int, optional): Initial recipe ID to load. Defaults to None.
            layout_mode (Literal["medium", "small"]): Initial layout mode. Defaults to "medium".
            selection (bool): Flag for selection mode (currently unused). Defaults to False.
        """
        super().__init__(parent)
        self.setObjectName("RecipeWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._recipe_id: Optional[int] = None
        self._recipe_data: Optional[Recipe] = None
        self._layout_mode: Literal["medium", "small"] = layout_mode
        self._selection: bool = selection
        self._current_content_widget: Optional[QWidget] = None # Track the current frame

        #🔹Main Layout🔹
        self._stacked_layout = QStackedLayout(self)
        self._stacked_layout.setContentsMargins(0, 0, 0, 0)
        # StackAll might not be needed if we always remove the old widget
        # self._stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.setLayout(self._stacked_layout)

         #🔹Styling & Initial State🔹
        # Load and apply the stylesheet ONCE during initialization
        stylesheet_content = load_and_apply_stylesheet(self, "stylesheet")
        if (stylesheet_content):
            self.setStyleSheet(stylesheet_content)
        else:
            DebugLogger.log("Stylesheet content is empty, not applying.", "warning")

        self.setProperty("layoutMode", self._layout_mode) # Set initial property for styling
        # Call set_layout_mode first to set constraints before setting recipe_id
        self.set_layout_mode(self._layout_mode)
        # Now set recipe_id, which will load data and build the initial frame
        self.set_recipe_id(recipe_id)

        DebugLogger.log(f"RecipeWidget initialized. Mode: {self._layout_mode}, ID: {self._recipe_id}", "info")

     #🔹Properties🔹
    def get_layout_mode(self) -> Literal["medium", "small"]:
        return self._layout_mode

    def set_layout_mode(self, mode: Literal["medium", "small"]):
        """Sets the layout mode and updates size constraints and stylesheet property."""
        if mode not in ["medium", "small"]:
            DebugLogger.log(f"Invalid layout mode '{mode}'. Defaulting to 'medium'.", "warning")
            mode = "medium"

        # Only update if mode actually changes
        if self._layout_mode == mode:
            self._update_size_constraints() # Ensure constraints are set even if mode doesn't change
            return

        self._layout_mode = mode
        self.setProperty("layoutMode", self._layout_mode) # Update property for QSS

         #🔹Re-evaluate Styles🔹
        self.style().unpolish(self)
        self.style().polish(self)

        self._update_size_constraints()
        # Only rebuild content if a recipe is actually loaded, otherwise size change is enough
        if self._recipe_id is not None:
            self._update_content()
        DebugLogger.log(f"Layout mode changed to: {self._layout_mode}", "info")

    def get_recipe_id(self) -> Optional[int]:
        return self._recipe_id

    def set_recipe_id(self, recipe_id: Optional[int]):
        """Sets the recipe ID and triggers a UI update."""
        if self._recipe_id == recipe_id:
            return # No change

        DebugLogger.log(f"Setting recipe ID to: {recipe_id}", "info")
        self._recipe_id = recipe_id
        self._recipe_data = None # Clear old data

        if self._recipe_id is not None:
            if not self._load_recipe():
                # If loading fails, revert to empty state
                self._recipe_id = None
                self._recipe_data = None

        self._update_content() # Update the displayed frame

     #🔹Internal Methods🔹
    def _update_size_constraints(self):
        """Applies fixed size based on the current layout mode."""
        if self._layout_mode == "medium":
            self.setFixedSize(MEDIUM_CARD_WIDTH, MEDIUM_CARD_HEIGHT)
        elif self._layout_mode == "small":
            self.setFixedSize(SMALL_CARD_WIDTH, SMALL_CARD_HEIGHT)
        self.updateGeometry()

    def _load_recipe(self) -> bool:
        """Loads recipe data from the database using the current recipe_id."""
        if self._recipe_id is None:
            DebugLogger.log("Cannot load recipe: recipe_id is None.", "warning")
            return False

        DebugLogger.log(f"Loading recipe data for ID: {self._recipe_id}", "info")
        try:
            # Assuming DB_INSTANCE.get_recipe returns a dict or similar
            recipe_dict = DB_INSTANCE.get_recipe(self._recipe_id)
            if recipe_dict:
                self._recipe_data = Recipe(recipe_dict) # Convert dict to Recipe object
                DebugLogger.log(f"Recipe '{self._recipe_data.name}' loaded successfully.", "info")
                return True
            else:
                DebugLogger.log(f"Recipe ID {self._recipe_id} not found in database.", "error")
                return False
        except Exception as e:
            DebugLogger.log(f"Error loading recipe ID {self._recipe_id}: {e}", "error", exc_info=True)
            return False

    def _update_content(self):
        """Creates and displays the appropriate content frame based on state."""
        new_content_widget: Optional[QWidget] = None

         #🔹Determine which frame to build🔹
        if self._recipe_id is not None and self._recipe_data is not None:
            if self._layout_mode == "medium":
                # Call build_medium_frame 
                new_content_widget = build_medium_frame(self._recipe_data, self)
                DebugLogger.log(f"Building medium frame for recipe ID: {self._recipe_id}", "debug")
            elif self._layout_mode == "small":
                # Call build_small_frame 
                new_content_widget = build_small_frame(self._recipe_data, self)
                DebugLogger.log(f"Building small frame for recipe ID: {self._recipe_id}", "debug")
        else:
            # Build empty frame
            new_content_widget = build_empty_frame(self)
            DebugLogger.log("Building empty frame.", "debug")


         #🔹Switch Widgets in Stacked Layout🔹
        if new_content_widget:
            # Remove the old widget if it exists
            if self._current_content_widget:
                self._stacked_layout.removeWidget(self._current_content_widget)
                self._current_content_widget.deleteLater()
                DebugLogger.log("Old content widget removed and scheduled for deletion.", "debug")

            # Add the new widget and make it current
            self._stacked_layout.addWidget(new_content_widget)
            self._stacked_layout.setCurrentWidget(new_content_widget)
            self._current_content_widget = new_content_widget
            DebugLogger.log(f"New content widget ({type(new_content_widget).__name__}) added and set as current.", "debug")

            # Ensure the main widget is visible and update
            self.update()
            self.updateGeometry()
        else:
             DebugLogger.log("Failed to build new content widget.", "error")

    def _open_recipe_selection(self):
        """Opens the recipe selection dialog."""
        if self._selection:
             DebugLogger.log("Widget is in selection mode, cannot open dialog again.", "info")
             return

        DebugLogger.log("Opening recipe selection dialog.", "info")
        # Use the specific dialog for this widget
        dialog = RecipeSelectionDialog(self)
        if dialog.exec():
            selected_id = dialog.selected_recipe_id
            if selected_id is not None:
                DebugLogger.log(f"Recipe selected with ID: {selected_id}", "info")
                self.set_recipe_id(selected_id) # This triggers _update_content
                self.recipe_selected.emit(selected_id) # Emit signal
            else:
                DebugLogger.log("Recipe selection cancelled or failed.", "info")
        else:
            DebugLogger.log("Recipe selection dialog closed without selection.", "info")

    def _handle_content_click(self):
        """Handles clicks forwarded from the content frame (Medium/SmallRecipeFrame)."""
        if self._recipe_id is not None:
            DebugLogger.log(f"Content frame clicked for Recipe ID: {self._recipe_id}", "info")
            self.widget_clicked.emit(self._recipe_id) # Emit the main widget's signal
            # Open the full recipe view when the content frame is clicked
            self._open_full_recipe_view()
        else:
            DebugLogger.log("Content frame clicked, but no recipe ID is set.", "warning")

    def _open_full_recipe_view(self):
        """Opens the modal dialog to show the full recipe details."""
        if self._recipe_id is None:
            DebugLogger.log("Cannot open full recipe view: No recipe ID.", "warning")
            return

        DebugLogger.log(f"Opening full recipe view for ID: {self._recipe_id}", "info")
        try:
            # Use the specific FullRecipe dialog for this widget
            dialog = FullRecipe(self._recipe_id, self)
            dialog.exec()
        except Exception as e:
            DebugLogger.log(f"Error opening FullRecipe dialog: {e}", "error", exc_info=True)

    #🔹Public Methods🔹
    def clear_recipe(self):
        """Resets the widget to the empty state."""
        DebugLogger.log("Clearing recipe.", "info")
        self.set_recipe_id(None) # This triggers _update_content to show empty frame
        self.recipe_cleared.emit()
