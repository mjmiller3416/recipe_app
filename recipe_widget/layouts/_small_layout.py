# 🔸 Standard Library Imports
from typing import TYPE_CHECKING

# 🔸 Third-party Imports
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QSize

# 🔸 Local Imports
from core.helpers.ui_helpers import wrap_layout

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
    widget.setFixedSize(QSize(widget.MINI_CARD_WIDTH, widget.MINI_CARD_HEIGHT))

    # 🔹 Image
    widget.lbl_image = QLabel()
    widget.lbl_image.setObjectName("CardImageMini")
    widget.lbl_image.setFixedSize(widget.MINI_IMAGE_SIZE)
    widget.lbl_image.setScaledContents(True)

    # 🔹 Title
    widget.lbl_name = QLabel()
    widget.lbl_name.setObjectName("CardTitleMini")
    widget.lbl_name.setWordWrap(True)
    # Center the text horizontally and vertically within the label
    widget.lbl_name.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)

    # ───── Mini Layout Wrapper ─────
    # Ensure wrap_layout is accessible via widget or imported directly
    mini_container, mini_layout = wrap_layout(QHBoxLayout, "MiniLayoutRoot")
    # Set margins to 0 for top, left, and bottom to make image flush
    # Keep right margin if needed for title spacing, or set to 0 as well.
    # Using constants for clarity, assuming they might be adjusted later.
    # Let's set all to 0 for edge-to-edge image on T/L/B.
    mini_layout.setContentsMargins(
        0, # widget.MINI_LAYOUT_MARGIN_LEFT (set to 0)
        0, # widget.MINI_LAYOUT_MARGIN_TOP (set to 0)
        widget.MINI_LAYOUT_MARGIN_RIGHT, # Keep right margin for now (was 0)
        0  # widget.MINI_LAYOUT_MARGIN_BOTTOM (set to 0)
    )
    mini_layout.setSpacing(widget.MINI_LAYOUT_SPACING)
    mini_layout.addWidget(widget.lbl_image)
    mini_layout.addWidget(widget.lbl_name)

    # ───── Main Layout ─────
    outer = QVBoxLayout(widget) # Set layout on the parent widget
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)
    outer.addWidget(mini_container)
