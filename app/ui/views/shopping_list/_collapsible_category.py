"""app/ui/views/shopping_list/collapsible_category.py

Collapsible category widget for organizing shopping items.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.style.icon.config import Icon
from app.ui.components.layout.card import BaseCard
from app.ui.components.widgets.button import BaseButton, ToolButton, Type
from app.ui.constants import LayoutConstants

class CollapsibleCategory(BaseCard):
    """Collapsible category widget for organizing shopping items.

    Displays a category header that can be clicked to expand/collapse
    its contents. Contains shopping items grouped by category with
    smooth animation transitions.

    Signals:
        toggled: Emitted when expansion state changes.
        itemChecked: Emitted when an item's checkbox state changes.
    """
    toggled = Signal(bool)
    itemChecked = Signal(str, bool)

    def __init__(self, category_name, parent=None, start_expanded=False):
        """Initialize the collapsible category widget.

        Args:
            category_name: Display name for the category.
            parent: Optional parent widget.
            start_expanded: Whether to start in expanded state.
        """
        super().__init__(parent)
        self._category_name = category_name
        self._is_expanded = start_expanded
        self._items = []

        self._setup_header()
        self._setup_content_area()
        self._setup_animation()

        # Force initial collapsed state to prevent layout flash on load
        if not start_expanded:
            self._content_container.setMaximumHeight(0)
            self._content_container.setVisible(False)

        self._update_expand_state(animate=False)

    # ── UI Setup Methods ────────────────────────────────────────────────────────────────────────────────────

    def _setup_header(self):
        """Create the clickable category header with expand button."""
        self._header_widget = QWidget()
        self._header_widget.setObjectName("CategoryHeader")

        header_layout = QHBoxLayout(self._header_widget)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(8)

        # Category label
        self._category_label = QLabel(self._category_name)
        self._category_label.setObjectName("CategoryLabel")

        # Expand button
        self._expand_button = ToolButton(Type.PRIMARY, Icon.ANGLE_DOWN)
        self._expand_button.setIconSize(24, 24)
        self._expand_button.setObjectName("ExpandButton")
        self._expand_button.clicked.connect(self.toggle)

        header_layout.addWidget(self._category_label)
        header_layout.addStretch()
        header_layout.addWidget(self._expand_button)

        # Make entire header clickable for better UX
        self._header_widget.mousePressEvent = lambda e: self.toggle()
        self._header_widget.setCursor(Qt.PointingHandCursor)

        self.addWidget(self._header_widget)

    def _setup_content_area(self):
        """Create the collapsible content area for shopping items."""
        self._content_container = QWidget()
        self._content_container.setObjectName("ContentContainer")

        self._items_layout = QVBoxLayout(self._content_container)
        self._items_layout.setContentsMargins(16, 8, 16, 12)
        self._items_layout.setSpacing(8)

        self.addWidget(self._content_container)

    def _setup_animation(self):
        """Configure smooth animation for expand/collapse transitions."""
        self._animation = QPropertyAnimation(self._content_container, b"maximumHeight")
        self._animation.setDuration(LayoutConstants.EXPAND_COLLAPSE_DURATION)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    # ── State Management ────────────────────────────────────────────────────────────────────────────────────

    def _update_expand_state(self, animate=True):
        """Update visual state based on expansion.

        Args:
            animate: Whether to animate the transition.
        """
        if self._is_expanded:
            self._expand_content(animate)
        else:
            self._collapse_content(animate)

        self._update_expand_button()

    def _expand_content(self, animate=True):
        """Expand the content area to show items.

        Args:
            animate: Whether to animate the expansion.
        """
        self._content_container.setVisible(True)

        if animate:
            # Calculate target height before animation to prevent visual glitches
            natural_height = self._content_container.sizeHint().height()

            self._animation.setStartValue(0)
            self._animation.setEndValue(natural_height)
            self._animation.finished.connect(
                lambda: self._content_container.setMaximumHeight(LayoutConstants.MAX_WIDGET_HEIGHT),
                Qt.SingleShotConnection
            )
            self._animation.start()
        else:
            self._content_container.setMaximumHeight(LayoutConstants.MAX_WIDGET_HEIGHT)

    def _collapse_content(self, animate=True):
        """Collapse the content area to hide items.

        Args:
            animate: Whether to animate the collapse.
        """
        if animate:
            current_height = self._content_container.height()
            self._animation.setStartValue(current_height)
            self._animation.setEndValue(0)
            self._animation.finished.connect(
                lambda: self._content_container.setVisible(False),
                Qt.SingleShotConnection
            )
            self._animation.start()
        else:
            self._content_container.setMaximumHeight(0)
            self._content_container.setVisible(False)

    def _update_expand_button(self):
        """Update expand button icon based on current state."""
        if self._is_expanded:
            icon_name = Icon.ANGLE_DOWN
            self._header_widget.setProperty("is_expanded", "True")
        else:
            icon_name = Icon.ANGLE_RIGHT
            self._header_widget.setProperty("is_expanded", "False")
        BaseButton.setIcon(self._expand_button, icon_name)

        # Qt workaround: force style refresh after property change
        self._header_widget.style().polish(self._header_widget)

        self._expand_button.setStateIconSize(24, 24)

    # ── Properties ──────────────────────────────────────────────────────────────────────────────────────────

    @property
    def category_name(self) -> str:
        """Get the category name."""
        return self._category_name

    @property
    def is_expanded(self) -> bool:
        """Check if category is currently expanded."""
        return self._is_expanded

    # ── Public Interface ────────────────────────────────────────────────────────────────────────────────────

    def toggle(self):
        """Toggle between expanded and collapsed states."""
        self._is_expanded = not self._is_expanded
        self._update_expand_state(animate=True)
        self.toggled.emit(self._is_expanded)

    def expand(self):
        """Expand the category if currently collapsed."""
        if not self._is_expanded:
            self.toggle()

    def collapse(self):
        """Collapse the category if currently expanded."""
        if self._is_expanded:
            self.toggle()

    def addItem(self, item_name: str) -> QCheckBox:
        """Add a simple checkbox item to the category.

        Args:
            item_name: Display text for the item.

        Returns:
            The created checkbox widget.
        """
        checkbox = QCheckBox(item_name)
        checkbox.stateChanged.connect(lambda state: self.itemChecked.emit(item_name, state == Qt.Checked))
        self._items_layout.addWidget(checkbox)
        self._items.append(checkbox)
        return checkbox

    def addShoppingItem(self, shopping_item_widget: QWidget) -> None:
        """Add a ShoppingItem widget to the category.

        Args:
            shopping_item_widget: The shopping item widget to add.
        """
        self._items_layout.addWidget(shopping_item_widget)
        self._items.append(shopping_item_widget)

    def setAllItemsChecked(self, checked: bool) -> None:
        """Check or uncheck all items in this category.

        Args:
            checked: Whether items should be checked.
        """
        for item in self._items:
            if isinstance(item, QCheckBox):
                item.setChecked(checked)
            elif hasattr(item, 'checkbox'):
                item.checkbox.setChecked(checked)

    def getCheckedItems(self) -> list[str]:
        """Get names of all checked items in this category.

        Returns:
            List of checked item names.
        """
        checked_items = []
        for item in self._items:
            if isinstance(item, QCheckBox) and item.isChecked():
                checked_items.append(item.text())
            elif hasattr(item, 'checkbox') and item.checkbox.isChecked():
                if hasattr(item, 'item') and hasattr(item.item, 'ingredient_name'):
                    checked_items.append(item.item.ingredient_name)
        return checked_items

    def cleanup(self) -> None:
        """Clean up all item widgets to prevent memory leaks.

        Called when the category is being destroyed or refreshed.
        Ensures proper cleanup of signal connections.
        """
        for item in self._items:
            if hasattr(item, 'cleanup'):
                item.cleanup()
        self._items.clear()
