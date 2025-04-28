# recipe_widget/frame_layouts/build_small_frame.py
# 🔸 Standard Library Imports
from typing import TYPE_CHECKING

from PySide6.QtGui import QMouseEvent  # For mousePressEvent

from helpers.debug_logger import DebugLogger
# 🔸 Third-party Imports
from core.helpers.qt_imports import QFrame, QHBoxLayout, QLabel, QSize, Qt
from core.helpers.ui_helpers import set_scaled_image
# 🔸 Local Imports
from core.modules.recipe_module import \
    Recipe  # Assuming Recipe object is passed

from ..config import SMALL_IMAGE_SIZE  # Import dimensions

# 🔸 Type Checking Imports
if TYPE_CHECKING:
    from ..recipe_widget import \
        RecipeWidget  # Import RecipeWidget for type hinting parent


class SmallRecipeFrame(QFrame):
    """A self-contained frame displaying a recipe in small format."""
    def __init__(self, recipe_data: Recipe, parent_widget: 'RecipeWidget'):
        super().__init__(parent_widget) # Parent is the RecipeWidget
        self.recipe_data = recipe_data
        self.parent_widget = parent_widget # Store reference to parent for click handling
        self.setObjectName("SmallRecipeFrame") # For potential styling

        # Build the internal UI of this frame
        self._build_internal_ui()
        self._populate_internal_ui()

    def _build_internal_ui(self):
        """Builds the widgets and layout *inside* this frame."""
        # 🔹 Image
        self.lbl_image = QLabel()
        self.lbl_image.setObjectName("CardImage")
        # Size is set during population
        self.lbl_image.setScaledContents(False)

        # 🔹 Title
        self.lbl_name = QLabel()
        self.lbl_name.setObjectName("CardTitle")
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # ───── Main Layout (for this frame) ─────
        main_layout = QHBoxLayout(self) # Set layout directly on the frame
        main_layout.setContentsMargins(0, 0, 8, 0)
        main_layout.setSpacing(8)
        main_layout.addWidget(self.lbl_image)
        main_layout.addWidget(self.lbl_name, 1) # Title stretches

        self.setLayout(main_layout)

    def _populate_internal_ui(self):
        """Populates the widgets *inside* this frame with recipe data."""
        if not self.recipe_data:
            DebugLogger.log("SmallRecipeFrame: Cannot populate, recipe_data is None.", "warning")
            return

        # Name
        self.lbl_name.setText(self.recipe_data.name)
        self.lbl_name.setToolTip(self.recipe_data.name)

        # Image
        target_size = SMALL_IMAGE_SIZE
        if self.recipe_data.has_image():
            set_scaled_image(self.lbl_image, self.recipe_data.image_path, target_size)
        else:
            set_scaled_image(self.lbl_image, None, target_size, fallback_text="No Img")

    def mousePressEvent(self, event: QMouseEvent):
        """Handles clicks on the frame to notify the parent RecipeWidget."""
        if event.button() == Qt.LeftButton:
            # Notify the parent RecipeWidget to handle the click (e.g., open full view)
            self.parent_widget._handle_content_click()
        super().mousePressEvent(event)


def build_small_frame(recipe_data: Recipe, parent_widget: 'RecipeWidget') -> SmallRecipeFrame:
    """
    Factory function to create and return a SmallRecipeFrame.

    Args:
        recipe_data (Recipe): The recipe data object.
        parent_widget (RecipeWidget): The parent RecipeWidget instance.

    Returns:
        SmallRecipeFrame: The constructed and populated frame.
    """
    return SmallRecipeFrame(recipe_data, parent_widget)
