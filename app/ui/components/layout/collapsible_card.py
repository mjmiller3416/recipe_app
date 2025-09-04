"""app/ui/components/layout/collapsible_card.py

A Card widget with collapsible functionality for shopping list categories.
"""

from typing import List, Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from _dev_tools.debug_logger import DebugLogger
from app.config import CARD
from app.style import Qss, Theme
from app.style.animation.animator import Animator
from app.style.icon import Name, Type
from app.ui.components.widgets.button import ToolButton
from .card import BaseCard

# ── Constants ────────────────────────────────────────────────────────────────────────────────
EXPANDED_HEIGHT = 300    # Full height when expanded
COLLAPSED_HEIGHT = 80    # Height when collapsed (header visible) - increased for more spacing
DURATION = 300           # Animation duration


# ── Collapsible Card Widget ──────────────────────────────────────────────────────────────────
class CollapsibleCard(BaseCard):
    """A Card widget with collapsible functionality for shopping list categories.

    This class extends the standard Card widget with collapsible behavior for
    organizing shopping list items by category. It includes checkable items
    and category management functionality.
    """

    # Signals
    toggled = Signal(bool)
    itemChecked = Signal(str, bool)

    def __init__(self, category_name: str, parent=None, start_expanded: bool = False):
        """Initialize the CollapsibleCard widget.

        Args:
            category_name: The display name for this category
            parent: Optional parent widget.
            start_expanded: Whether to start in expanded state
        """
        super().__init__(parent, content_layout="vbox", card_type="Default")

        self.setObjectName("CollapsibleCard")

        # Register for collapsible card specific styling
        Theme.register_widget(self, Qss.COLLAPSIBLE_CARD)

        # Category properties
        self._category_name = category_name
        self._items: List[QCheckBox] = []

        # Set up like sidebar - fixed initial size and state
        self.setMinimumHeight(0)
        self.setMaximumHeight(EXPANDED_HEIGHT)
        self._is_expanded = start_expanded
        self._collapse_button = None

        # Set header with category name
        self.setHeader(category_name)

    def _add_collapse_button_to_header(self):
        """Add the collapse button to the right side of the header."""
        if not self._header_row_layout or not self._collapse_button:
            return

        # Add stretch to push button to the right
        self._header_row_layout.addStretch()

        # Add the collapse button aligned to the right
        self._header_row_layout.addWidget(
            self._collapse_button,
            0,
            Qt.AlignVCenter | Qt.AlignRight
        )

    def _create_collapse_button(self):
        """Create the collapse/expand toggle button."""
        if self._collapse_button:
            return

        self._collapse_button = ToolButton(Type.DEFAULT, Name.ANGLE_DOWN)
        self._collapse_button.setObjectName("CollapseButton")
        self._collapse_button.clicked.connect(self.toggle)
        self._collapse_button.setFixedSize(24, 24)

        DebugLogger.log("Created collapse button for collapsible card", "debug")

    def _update_collapse_button_icon(self):
        """Update the collapse button icon based on expanded state."""
        if not self._collapse_button:
            return

        from app.ui.components.widgets.button import BaseButton

        BaseButton.swapIcon(self._collapse_button, self._is_expanded, Name.ANGLE_DOWN, Name.ANGLE_RIGHT)


    # ── Public API ───────────────────────────────────────────────────────────────────────────────
    @property
    def is_expanded(self) -> bool:
        """Check if the card is currently expanded."""
        return self._is_expanded

    @property
    def animation_duration(self) -> int:
        """Get the current animation duration."""
        return self._animation_duration

    def setAnimationDuration(self, duration: int):
        """Set the animation duration for expand/collapse.

        Args:
            duration: Animation duration in milliseconds.
        """
        self._animation_duration = duration

    def setExpanded(self, expanded: bool, animate: bool = True):
        """Programmatically set the expanded state.

        Args:
            expanded: Whether the card should be expanded.
            animate: Whether to animate the state change.
        """
        if self._is_expanded == expanded:
            return  # Already in the desired state

        if animate:
            self.toggle()
        else:
            # Set state without animation - use fixed heights like sidebar
            self._is_expanded = expanded
            self._update_collapse_button_icon()

            # Set the card height directly using our constants
            if expanded:
                self.setMaximumHeight(EXPANDED_HEIGHT)
            else:
                self.setMaximumHeight(COLLAPSED_HEIGHT)

    def setHeader(self, text: str, icon: Optional[object] = None):
        """Override setHeader to add collapse button to header.

        Args:
            text: Header text.
            icon: Optional icon (Name enum or QWidget).
        """
        # Call parent setHeader first
        super().setHeader(text, icon)

        # Add collapse button to header
        self._create_collapse_button()
        self._add_collapse_button_to_header()

    def toggle(self):
        """Toggle the collapsed/expanded state - exact copy of sidebar logic."""
        DebugLogger.log(
            f"Toggling collapsible card: currently {'expanded' if self._is_expanded else 'collapsed'}"
        )

        start = self.maximumHeight()
        end = COLLAPSED_HEIGHT if self._is_expanded else EXPANDED_HEIGHT
        duration = DURATION

        # Ensure header stays at natural size during animation
        if self._header_container:
            natural_header_height = self._header_container.sizeHint().height()
            self._header_container.setMinimumHeight(natural_header_height)
            self._header_container.setMaximumHeight(natural_header_height)

        animation = Animator.animate_height(self, start, end, duration)

        # Only restore header flexibility when expanding
        def on_animation_complete():
            if self._is_expanded and self._header_container:
                # Restore flexible header when expanded
                self._header_container.setMinimumHeight(0)
                self._header_container.setMaximumHeight(16777215)

        animation.finished.connect(on_animation_complete)

        self._is_expanded = not self._is_expanded
        self._update_collapse_button_icon()
        self.toggled.emit(self._is_expanded)

    # ── Shopping List Methods ──────────────────────────────────────────────────────────
    def add_item(self, item_name: str, checked: bool = False) -> QCheckBox:
        """Add a checkable item to the category.

        Args:
            item_name: The display name for the item
            checked: Whether the item should start checked

        Returns:
            The created QCheckBox widget
        """
        checkbox = QCheckBox(item_name)
        checkbox.setObjectName("CategoryItem")
        checkbox.setChecked(checked)

        checkbox.toggled.connect(
            lambda state: self.itemChecked.emit(item_name, state)
        )

        self._items.append(checkbox)
        self.addWidget(checkbox)

        return checkbox

    def get_checked_items(self) -> List[str]:
        """Get list of checked item names."""
        return [cb.text() for cb in self._items if cb.isChecked()]

    def set_all_items_checked(self, checked: bool):
        """Set all items to checked/unchecked state."""
        for checkbox in self._items:
            checkbox.setChecked(checked)

    def clear_items(self):
        """Remove all items from the category."""
        for checkbox in self._items:
            self.removeWidget(checkbox)
            checkbox.deleteLater()
        self._items.clear()

    @property
    def category_name(self) -> str:
        """Get the category name."""
        return self._category_name

    @property
    def item_count(self) -> int:
        """Get the number of items in this category."""
        return len(self._items)

