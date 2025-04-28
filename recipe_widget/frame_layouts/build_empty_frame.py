# recipe_widget/frame_layouts/build_empty_frame.py
# 🔸 Standard Library Imports
from typing import TYPE_CHECKING

# 🔸 Local Imports
from core.application.config import icon_path
from helpers.debug_logger import DebugLogger
# 🔸 Third-party Imports
from core.helpers.qt_imports import (QFrame, QHBoxLayout, QIcon, QPushButton,
                                     QSize, Qt, QVBoxLayout)

# 🔸 Type Checking Imports
if TYPE_CHECKING:
    from ..recipe_widget import \
        RecipeWidget  # Import RecipeWidget for type hinting parent

def build_empty_frame(parent_widget: 'RecipeWidget') -> QFrame:
    """
    Builds the 'empty' frame containing the 'Add Meal' button.

    Args:
        parent_widget (RecipeWidget): The parent RecipeWidget instance (used for signal connection).

    Returns:
        QFrame: The constructed frame for the empty state.
    """
    empty_frame = QFrame(parent_widget)
    empty_frame.setObjectName("EmptyFrame") # For potential styling

    btn_add_meal = QPushButton(empty_frame)
    btn_add_meal.setObjectName("btnAddMeal")
    btn_add_meal.setFlat(True)
    try:
        add_icon = QIcon(icon_path("add_meal"))
        if add_icon.isNull():
             DebugLogger.log("Failed to load 'add_meal' icon.", "error")
             btn_add_meal.setText("+") # Fallback text
        else:
             btn_add_meal.setIcon(add_icon)
    except Exception as e:
        DebugLogger.log(f"Error loading 'add_meal' icon: {e}", "error")
        btn_add_meal.setText("+") # Fallback text

    btn_add_meal.setIconSize(QSize(50, 50))
    btn_add_meal.setCursor(Qt.PointingHandCursor)
    btn_add_meal.setToolTip("Click to select a recipe")
    # Connect directly to the parent widget's method that opens the dialog
    btn_add_meal.clicked.connect(parent_widget._open_recipe_selection)

    # Center the button within the frame
    center_layout = QHBoxLayout()
    center_layout.addStretch()
    center_layout.addWidget(btn_add_meal)
    center_layout.addStretch()

    main_layout = QVBoxLayout(empty_frame)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addLayout(center_layout)

    empty_frame.setLayout(main_layout)
    return empty_frame
