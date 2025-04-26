#🔸System Imports
from enum import Enum
from typing import Optional

#🔸Third-party Imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

#🔸Local Imports
from core.helpers.app_helpers import load_stylesheet_for_widget
from core.helpers.debug_logger import DebugLogger
from core.modules.recipe_module import Recipe


class LayoutSize(Enum):
    """
    Enum to define the target layout size for the RecipeWidget when displaying a recipe.
    """
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class TestRecipeWidget(QFrame):
    """
    A container widget that displays a recipe card or an 'empty state' prompt.
    Manages switching between an empty state (no recipe) and different recipe
    display sizes (small, medium, large) when a recipe is present.

    Signals:
        recipe_selected (Signal): Emitted when a recipe is chosen (placeholder for future use).
        recipe_cleared (Signal): Emitted when the recipe is cleared (placeholder for future use).
        widget_clicked (Signal): Emitted when the populated recipe frame is clicked.
        empty_widget_clicked = Signal(): Emitted when the button in the empty state is clicked.
    """
    # Keep signals if they are relevant to your application logic
    recipe_selected = Signal(int)
    recipe_cleared = Signal()
    widget_clicked = Signal(int) 
    empty_widget_clicked = Signal()

    def __init__(self, initial_size: LayoutSize = LayoutSize.MEDIUM, parent = None):
        """
        Initialize the TestRecipeWidget.

        Args:
            initial_size (LayoutSize): The initial target size for displaying recipes.
                                       Defaults to MEDIUM.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._main_layout = QVBoxLayout(self)
        self.setLayout(self._main_layout)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._recipe: Optional[Recipe] = None # Holds the current Recipe object or None
        self._current_layout_size: LayoutSize = initial_size
        self._current_frame: Optional[QFrame] = None # Keep track of the current displayed frame

        self._build_layout() # Build the initial state (will be empty)

        load_stylesheet_for_widget(self, "dev_sandbox/test_recipe_widget/stylesheet.qss")

    def _set_recipe(self, recipe: Optional[Recipe]) -> None:
        """
        Sets or clears the recipe and rebuilds the UI accordingly.
        Pass None to clear the recipe and show the empty state.

        Args:
            recipe (Recipe | None): The Recipe object to display, or None to clear.
        """
        if recipe is not self._recipe: # Check if recipe actually changed
            self._recipe = recipe
            recipe_id = recipe.id if recipe else "None"
            DebugLogger.log(f"Recipe set to ID: {recipe_id}. Rebuilding layout.", "info")
            self._build_layout()
            if recipe is None:
                self.recipe_cleared.emit() # Emit signal if recipe is cleared

    def _set_layout_size(self, size: LayoutSize | str) -> None:
        """
        Sets the desired layout size for displaying recipes and rebuilds the UI.

        Args:
            size (LayoutSize | str): The target layout size (enum member or string "small", "medium", "large").
        """
        if isinstance(size, str):
            try:
                size = LayoutSize(size.lower())
            except ValueError:
                DebugLogger.log(f"Invalid layout size string: {size}", "error")
                return
        elif not isinstance(size, LayoutSize):
             DebugLogger.log(f"Invalid layout size type: {type(size)}", "error")
             return

        if size is not self._current_layout_size: # Check if size actually changed
            self._current_layout_size = size
            DebugLogger.log(f"Layout size set to: {size.value}. Rebuilding layout.", "info")
            # Rebuild only if the size change affects the current view
            self._build_layout()

    def _current_recipe(self) -> Optional[Recipe]:
        """Returns the currently loaded Recipe object, or None."""
        return self._recipe

    def _clear_layout(self):
        """Safely clears the main layout by deleting the current frame if it exists."""
        if self._current_frame is not None:
            # Remove from layout first
            self._main_layout.removeWidget(self._current_frame)
            # Schedule for deletion
            self._current_frame.deleteLater()
            DebugLogger.log(f"Deleted widget: {self._current_frame.objectName()}", "info")
            self._current_frame = None

    def _build_layout(self) -> None:
        """Builds the layout based on recipe state and current layout size."""
        self._clear_layout() # Clear the previous frame

        frame: QFrame | None = None
        widget_state = "empty" # Default state name

        try:
            if self._recipe is None:
                #--- EMPTY STATE ---
                widget_state = "empty"
                DebugLogger.log(f"Building EMPTY state frame (context: {self._current_layout_size.value})", "info")
                frame = self._build_empty_state_frame(self._current_layout_size)

                # Connect button signal for empty state
                if isinstance(frame, QFrame) and (button := frame.findChild(QPushButton, "AddMealButton")):
                    button.clicked.connect(self.empty_widget_clicked.emit)

            else:
                #--- RECIPE STATE ---
                widget_state = "recipe"
                DebugLogger.log(f"Building RECIPE state frame using TestFrameBuilder (size: {self._current_layout_size.value})", "info")

                builder = TestFrameBuilder(layout_size=self._current_layout_size.value, recipe=self._recipe) #
                frame = builder.build() # build() returns the fully constructed QFrame
                # Set object name for the frame *after* it's created by the builder
                frame.setObjectName(f"RecipeFrame_{self._current_layout_size.value}")
                # Add mouse event handling for the recipe frame
                frame.mousePressEvent = self._on_widget_clicked

        except Exception as e:
            # Catch errors during frame building (either empty or recipe state)
            DebugLogger.log(f"Error building frame for state '{widget_state}', size '{self._current_layout_size.value}': {e}", "error", exc_info=True) # Log traceback
            widget_state = "error"
            frame = self._build_error_frame(f"Failed to build view:\n{e}")

        #--- Common Frame Handling ---
        if frame:
            self._current_frame = frame # Track the newly created frame
            # Set properties for potential styling (CSS) based on the final state
            frame.setProperty("layout_size", self._current_layout_size.value)
            frame.setProperty("widget_state", widget_state)

            # Ensure styles are applied/updated *after* properties are set
            frame.style().unpolish(frame)
            frame.style().polish(frame)

            self._main_layout.addWidget(frame)
            DebugLogger.log(f"Added frame '{frame.objectName()}' with state '{widget_state}'", "info")
        else:
             # This case indicates a problem in _build_empty_state_frame or _build_error_frame
             DebugLogger.log(f"No frame was created for state '{widget_state}' and size '{self._current_layout_size.value}'.", "critical")
             # Optionally create a minimal error frame here as a last resort
             fallback_error_frame = QFrame()
             fallback_error_frame.setObjectName("FallbackErrorFrame")
             fallback_error_frame.setLayout(QVBoxLayout())
             fallback_error_frame.layout().addWidget(QLabel("Critical build error!"))
             self._main_layout.addWidget(fallback_error_frame)
             self._current_frame = fallback_error_frame

    def _build_empty_state_frame(self, size_context: LayoutSize) -> QFrame:
        """Creates the widget to display when no recipe is loaded."""
        container_frame = QFrame()
        container_frame.setObjectName("EmptyStateFrame") # Set object name
        lyt = QVBoxLayout(container_frame)

        btn_add_meal = QPushButton() 
        btn_add_meal.setObjectName("AddMealButton") # Name for finding child later
        # Signal connection is handled in _build_layout after frame creation

        lyt.addStretch(1)
        lyt.addWidget(btn_add_meal, 0, Qt.AlignmentFlag.AlignCenter)
        lyt.addStretch(1)

        # Apply fixed size consistent with TestFrameBuilder using LAYOUT_SIZE constant
        fixed_size = LAYOUT_SIZE.get(size_context.value) #
        if fixed_size:
            container_frame.setFixedSize(fixed_size) #
        else:
            DebugLogger.log(f"No fixed size found in LAYOUT_SIZE for '{size_context.value}', empty frame will auto-size.", "warning")
            container_frame.setMinimumSize(100, 50) # Provide a fallback minimum

        return container_frame

    def _build_error_frame(self, error_message: str) -> QFrame:
         """Creates a simple frame to display an error message."""
         frame = QFrame()
         frame.setObjectName("ErrorStateFrame") # Set object name
         lyt = QVBoxLayout(frame)
         lbl = QLabel(f"Error:\n{error_message}")
         lbl.setWordWrap(True)
         lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
         lbl.setStyleSheet("color: red; margin: 5px;")
         lyt.addWidget(lbl)

         # Apply fixed size consistent with TestFrameBuilder using LAYOUT_SIZE constant
         fixed_size = LAYOUT_SIZE.get(self._current_layout_size.value) #
         if fixed_size:
             frame.setFixedSize(fixed_size) #
         else: # Fallback
             frame.setMinimumSize(100, 50)
         return frame

    def _on_widget_clicked(self, event):
        """Handles mouse press events on the recipe frame."""
        if event.button() == Qt.LeftButton and self._recipe:
            DebugLogger.log(f"Recipe widget clicked (ID: {self._recipe.id}). Emitting signal.", "info")
            self.widget_clicked.emit(self._recipe.id)
