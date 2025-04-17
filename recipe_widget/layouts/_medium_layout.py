# 🔸 Standard Library Imports
from typing import TYPE_CHECKING

# 🔸 Third-party Imports
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize

# 🔸 Local Imports
from core.helpers.ui_helpers import wrap_layout
from core.helpers import svg_loader
from core.helpers.config import icon_path, ICON_COLOR # Assuming ICON_COLOR is defined here

# 🔸 Type Checking Imports (Avoids Circular Import)
if TYPE_CHECKING:
    from ..recipe_widget import RecipeWidget # Import RecipeWidget for type hinting

def build_full_layout(widget: 'RecipeWidget'):
    """
    Builds the 'full' layout for the RecipeCard.
    Spacing and margins are handled here.

    Args:
        widget (RecipeWidget): The parent RecipeWidget instance.
    """
    widget.setFixedSize(QSize(widget.FULL_CARD_WIDTH, widget.FULL_CARD_HEIGHT))

    # 🔹 Image
    widget.lbl_image = QLabel()
    widget.lbl_image.setObjectName("CardImageFull")
    widget.lbl_image.setFixedSize(widget.FULL_CARD_WIDTH, widget.FULL_IMAGE_HEIGHT)
    widget.lbl_image.setScaledContents(True)

    # 🔹 Title
    widget.lbl_name = QLabel()
    widget.lbl_name.setObjectName("CardTitle")
    widget.lbl_name.setWordWrap(True)
    widget.lbl_name.setAlignment(Qt.AlignCenter)

    # ───── Servings Block ─────
    widget.lbl_servings_title = QLabel("Servings")
    widget.lbl_servings_title.setObjectName("ServingsTitle")
    widget.lbl_servings_title.setAlignment(Qt.AlignLeft)

    widget.servings_icon = QLabel()
    # Ensure svg_loader and icon_path are accessible via widget or imported directly
    widget.servings_icon.setPixmap(
        svg_loader(
            icon_path("servings"),
            ICON_COLOR, # Make sure ICON_COLOR is accessible
            QSize(40, 40),
            return_type=QPixmap,
            source_color="#000"
        )
    )
    widget.servings_icon.setObjectName("ServingsIcon")
    widget.servings_icon.setAlignment(Qt.AlignLeft)
    widget.servings_icon.setFixedSize(40, 40)

    widget.lbl_servings = QLabel()
    widget.lbl_servings.setObjectName("ServingsLabel")
    widget.lbl_servings.setAlignment(Qt.AlignLeft)

    servings_value_row = QHBoxLayout()
    servings_value_row.setContentsMargins(0, 0, 0, 0)
    servings_value_row.setSpacing(widget.SERVINGS_VALUE_ROW_SPACING)
    servings_value_row.setAlignment(Qt.AlignLeft)
    servings_value_row.addWidget(widget.servings_icon)
    servings_value_row.addWidget(widget.lbl_servings)

    servings_layout = QVBoxLayout()
    servings_layout.setContentsMargins(0, 0, 0, 0)
    servings_layout.setSpacing(widget.SERVINGS_TIME_LAYOUT_SPACING)
    servings_layout.setAlignment(Qt.AlignLeft)
    servings_layout.addWidget(widget.lbl_servings_title)
    servings_layout.addLayout(servings_value_row)

    # ───── Time Block ─────
    widget.lbl_time_title = QLabel("Time")
    widget.lbl_time_title.setObjectName("TimeTitle")
    widget.lbl_time_title.setAlignment(Qt.AlignRight)

    widget.lbl_time = QLabel()
    widget.lbl_time.setObjectName("TimeLabel")
    widget.lbl_time.setAlignment(Qt.AlignRight)

    time_layout = QVBoxLayout()
    time_layout.setContentsMargins(0, 0, 0, 0)
    time_layout.setSpacing(widget.SERVINGS_TIME_LAYOUT_SPACING)
    time_layout.setAlignment(Qt.AlignRight)
    time_layout.addWidget(widget.lbl_time_title)
    time_layout.addWidget(widget.lbl_time)

    # ───── Metadata Row (Servings + Time) ─────
    # Ensure wrap_layout is accessible via widget or imported directly
    widget.meta_container, meta_layout = wrap_layout(QHBoxLayout, "CardMetaRow")
    meta_layout.setContentsMargins(
        widget.META_LAYOUT_MARGIN_LEFT,
        widget.META_LAYOUT_MARGIN_TOP,
        widget.META_LAYOUT_MARGIN_RIGHT,
        widget.META_LAYOUT_MARGIN_BOTTOM
    )
    meta_layout.setSpacing(widget.META_LAYOUT_SPACING)
    meta_layout.addLayout(servings_layout)
    meta_layout.addStretch()
    meta_layout.addLayout(time_layout)

    # ───── Full Layout Wrapper ─────
    full_container, full_layout = wrap_layout(QVBoxLayout, "FullLayoutRoot")
    full_layout.setContentsMargins(0, 0, 0, 0)
    full_layout.setSpacing(widget.FULL_LAYOUT_SPACING)
    full_layout.addWidget(widget.lbl_image)
    full_layout.addWidget(widget.lbl_name)
    full_layout.addWidget(widget.meta_container)

    # ───── Main Layout ─────
    outer = QVBoxLayout(widget) # Set layout on the parent widget
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)
    outer.addWidget(full_container)
