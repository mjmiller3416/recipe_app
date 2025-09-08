
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.constants import LayoutConstants
from app.core.utils.text_utils import sanitize_multiline_input
from app.ui.utils.widget_utils import apply_object_name_pattern

class DirectionsList(QWidget):
    """A numbered list widget for displaying recipe directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DirectionsList")

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(LayoutConstants.DIRECTIONS_LIST_SPACING)

    def setDirections(self, directions: str):
        """Set the directions to display."""
        # Clear existing directions
        self._clearDirections()

        # Parse directions using text sanitization utility
        sanitized_directions = sanitize_multiline_input(directions) if directions else ""
        steps = sanitized_directions.splitlines() if sanitized_directions else []

        if not steps:
            empty_label = QLabel("No directions available.")
            empty_label.setObjectName("EmptyDirections")
            empty_label.setWordWrap(True)
            self.layout.addWidget(empty_label)
        else:
            # Add numbered steps
            for i, step in enumerate(steps, start=1):
                self._addDirectionItem(i, step)

    def _clearDirections(self):
        """Clear all direction items from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _addDirectionItem(self, number: int, text: str):
        """Add a single direction item to the list."""
        # Create direction row widget with utility
        item_widget = QWidget()
        apply_object_name_pattern(item_widget, "Direction", "Item")

        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(LayoutConstants.DIRECTIONS_ITEM_SPACING)

        # Create standardized labels
        number_label = self._create_direction_label(
            f"{number}.", "Direction", "Number",
            Qt.AlignLeft | Qt.AlignTop, min_width=LayoutConstants.DIRECTIONS_NUMBER_WIDTH
        )
        text_label = self._create_direction_label(
            text, "Direction", "Text",
            Qt.AlignLeft | Qt.AlignTop, word_wrap=True
        )

        # Add to layout
        item_layout.addWidget(number_label)
        item_layout.addWidget(text_label, 1)

        # Add to main layout
        self.layout.addWidget(item_widget)

    def _create_direction_label(self, text: str, context: str, label_type: str,
                              alignment: Qt.AlignmentFlag, min_width: int = None,
                              word_wrap: bool = False) -> QLabel:
        """Create a standardized direction label with consistent styling."""
        label = QLabel(text)
        apply_object_name_pattern(label, context, label_type)
        label.setAlignment(alignment)
        if min_width:
            label.setMinimumWidth(min_width)
        if word_wrap:
            label.setWordWrap(True)
        return label
