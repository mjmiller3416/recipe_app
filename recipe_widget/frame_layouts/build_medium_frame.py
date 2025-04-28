# recipe_widget/frame_layouts/build_medium_frame.py
# 🔸 Standard Library Imports
from typing import TYPE_CHECKING

# 🔸 Third-party Imports
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from core.application.config import ICON_COLOR, icon_path
from core.helpers.debug_logger import DebugLogger
from core.helpers.ui_helpers import set_scaled_image, svg_loader
# 🔸 Local Imports
from core.modules.recipe_module import Recipe

from ..config import MEDIUM_CARD_WIDTH  # Import dimensions
from ..config import MEDIUM_IMAGE_HEIGHT

# 🔸 Type Checking Imports
if TYPE_CHECKING:
    from ..recipe_widget import \
        RecipeWidget  # Import RecipeWidget for type hinting parent


class MediumRecipeFrame(QFrame):
    """A self-contained frame displaying a recipe in medium format."""
    def __init__(self, recipe_data: Recipe, parent_widget: 'RecipeWidget'):
        super().__init__(parent_widget) # Parent is the RecipeWidget
        self.recipe_data = recipe_data
        self.parent_widget = parent_widget # Store reference to parent for click handling
        self.setObjectName("MediumRecipeFrame") # For potential styling

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
        self.lbl_name.setAlignment(Qt.AlignCenter)

        title_container = QHBoxLayout()
        # Sets padding (left, top, right, bottom) around the title label within its container
        title_container.setContentsMargins(16, 8, 16, 0)
        title_container.addWidget(self.lbl_name)

        # ───── Servings Block ─────
        lbl_servings_title = QLabel("Servings")
        lbl_servings_title.setObjectName("ServingsTitle")
        lbl_servings_title.setAlignment(Qt.AlignLeft)

        self.servings_icon = QLabel()
        self.servings_icon.setObjectName("ServingsIcon")
        self.servings_icon.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.servings_icon.setFixedSize(40, 40)

        self.lbl_servings = QLabel()
        self.lbl_servings.setObjectName("ServingsLabel")
        self.lbl_servings.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        servings_value_row = QHBoxLayout()
        # Sets padding (left, top, right, bottom) within the servings icon+label row
        servings_value_row.setContentsMargins(0, 0, 0, 0)
        # Sets spacing between items (icon and label) in the servings row
        servings_value_row.setSpacing(8)
        servings_value_row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        servings_value_row.addWidget(self.servings_icon)
        servings_value_row.addWidget(self.lbl_servings)
        servings_value_row.addStretch()

        servings_layout = QVBoxLayout()
        # Sets padding (left, top, right, bottom) around the entire servings block (title + value row)
        servings_layout.setContentsMargins(0, 0, 0, 0)
        # Sets vertical spacing between the servings title and the value row
        servings_layout.setSpacing(2)
        servings_layout.addWidget(lbl_servings_title)
        servings_layout.addLayout(servings_value_row)

        # ───── Time Block ─────
        lbl_time_title = QLabel("Time")
        lbl_time_title.setObjectName("TimeTitle")
        lbl_time_title.setAlignment(Qt.AlignRight)

        self.lbl_time = QLabel()
        self.lbl_time.setObjectName("TimeLabel")
        self.lbl_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        time_value_row = QHBoxLayout()
        # Sets padding (left, top, right, bottom) within the time label row
        time_value_row.setContentsMargins(0, 0, 0, 0)
        # Sets spacing between items (stretch and label) in the time row
        time_value_row.setSpacing(4)
        time_value_row.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        time_value_row.addStretch()
        time_value_row.addWidget(self.lbl_time)

        time_layout = QVBoxLayout()
        # Sets padding (left, top, right, bottom) around the entire time block (title + value row)
        time_layout.setContentsMargins(0, 0, 0, 0)
        # Sets vertical spacing between the time title and the value row
        time_layout.setSpacing(2)
        time_layout.setAlignment(Qt.AlignRight)
        time_layout.addWidget(lbl_time_title)
        time_layout.addLayout(time_value_row)

        # ───── Metadata Row ─────
        meta_layout = QHBoxLayout()
        # Sets padding (left, top, right, bottom) around the combined servings and time blocks
        meta_layout.setContentsMargins(16, 8, 16, 0)
        # Sets horizontal spacing between the servings block and the time block
        meta_layout.setSpacing(16)
        meta_layout.addLayout(servings_layout)
        meta_layout.addLayout(time_layout)

        # ───── Main Layout (for this frame) ─────
        main_layout = QVBoxLayout(self) # Set layout directly on the frame
        # Sets padding (left, top, right, bottom) for the entire frame content
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Sets vertical spacing between the main elements (image, title container, metadata layout)
        main_layout.setSpacing(8)
        main_layout.addWidget(self.lbl_image)
        main_layout.addLayout(title_container)
        main_layout.addLayout(meta_layout)
        main_layout.addStretch(1) # Pushes content up if there's extra vertical space

        self.setLayout(main_layout)

    def _populate_internal_ui(self):
        """Populates the widgets *inside* this frame with recipe data."""
        if not self.recipe_data:
            DebugLogger.log("MediumRecipeFrame: Cannot populate, recipe_data is None.", "warning")
            return

        # Name
        self.lbl_name.setText(self.recipe_data.name)
        self.lbl_name.setToolTip(self.recipe_data.name)

        # Image
        target_size = QSize(MEDIUM_CARD_WIDTH, MEDIUM_IMAGE_HEIGHT)
        if self.recipe_data.has_image():
            set_scaled_image(self.lbl_image, self.recipe_data.image_path, target_size)
        else:
            set_scaled_image(self.lbl_image, None, target_size, fallback_text="No Image")

        # Servings
        self.lbl_servings.setText(self.recipe_data.formatted_servings())
        icon_size = QSize(40, 40)
        try:
            pixmap = svg_loader(icon_path("servings"), ICON_COLOR, icon_size, return_type=QPixmap)
            if pixmap and not pixmap.isNull():
                self.servings_icon.setPixmap(pixmap)
            else:
                self.servings_icon.setText("?")
        except Exception as e:
            DebugLogger.log(f"Error loading servings icon: {e}", "error")
            self.servings_icon.setText("?")

        # Time
        self.lbl_time.setText(self.recipe_data.formatted_time())

    def mousePressEvent(self, event: QMouseEvent):
        """Handles clicks on the frame to notify the parent RecipeWidget."""
        if event.button() == Qt.LeftButton:
            # Notify the parent RecipeWidget to handle the click (e.g., open full view)
            self.parent_widget._handle_content_click()
        super().mousePressEvent(event)


def build_medium_frame(recipe_data: Recipe, parent_widget: 'RecipeWidget') -> MediumRecipeFrame:
    """
    Factory function to create and return a MediumRecipeFrame.

    Args:
        recipe_data (Recipe): The recipe data object.
        parent_widget (RecipeWidget): The parent RecipeWidget instance.

    Returns:
        MediumRecipeFrame: The constructed and populated frame.
    """
    return MediumRecipeFrame(recipe_data, parent_widget)
