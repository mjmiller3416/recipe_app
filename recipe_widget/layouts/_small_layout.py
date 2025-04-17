# 🔸 Standard Library Imports
from typing import TYPE_CHECKING

# 🔸 Third-party Imports
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QSize

# 🔸 Local Imports
from core.helpers.ui_helpers import wrap_layout
# Import constants from the parent directory's config
from .._config import (
    MINI_CARD_WIDTH, MINI_CARD_HEIGHT, MINI_IMAGE_SIZE,
    MINI_LAYOUT_MARGIN_LEFT, MINI_LAYOUT_MARGIN_TOP,
    MINI_LAYOUT_MARGIN_RIGHT, MINI_LAYOUT_MARGIN_BOTTOM,
    MINI_LAYOUT_SPACING
)

# 🔸 Type Checking Imports (Avoids Circular Import)
if TYPE_CHECKING: 
    from ..recipe_widget import RecipeWidget # Import RecipeWidget for type hinting

def build_mini_layout(widget: 'RecipeWidget'): # Add type hint using quotes
    """
    Builds the 'mini' layout for the RecipeCard.
    Spacing and margins are now handled here.

    Args:
        widget (RecipeWidget): The parent RecipeWidget instance.
    """
    widget.setFixedSize(QSize(MINI_CARD_WIDTH, MINI_CARD_HEIGHT))

    # 🔹 Image
    widget.lbl_image = QLabel()
    widget.lbl_image.setObjectName("CardImageMini")
    widget.lbl_image.setFixedSize(MINI_IMAGE_SIZE)
    widget.lbl_image.setScaledContents(True)

    # 🔹 Title
    widget.lbl_name = QLabel()
    widget.lbl_name.setObjectName("CardTitleMini")
    widget.lbl_name.setWordWrap(True)
    # Center the text horizontally and vertically within the label
    widget.lbl_name.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)

    # ───── Mini Layout Wrapper ─────
    mini_container, mini_layout = wrap_layout(QHBoxLayout, "MiniLayoutRoot")
    # Set Margins to 0 for edge-to-edge image on T/L/B.
    mini_layout.setContentsMargins(
        MINI_LAYOUT_MARGIN_LEFT,
        MINI_LAYOUT_MARGIN_TOP,
        MINI_LAYOUT_MARGIN_RIGHT,
        MINI_LAYOUT_MARGIN_BOTTOM
    )
    mini_layout.setSpacing(MINI_LAYOUT_SPACING)
    mini_layout.addWidget(widget.lbl_image)
    mini_layout.addWidget(widget.lbl_name)

    # ───── Main Layout ─────
    # Create the main layout without setting it on the widget here
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    main_layout.addWidget(mini_container)
    return main_layout # Return the constructed layout
