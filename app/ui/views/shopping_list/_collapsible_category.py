"""app/ui/views/shopping_list/_collapsible_category.py

This module defines the CollapsibleCategory widget, which represents a category in the shopping list
that can be expanded or collapsed to show or hide its items.
"""

# ── Imports ──
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.style.icon import Icon, Type
from app.ui.components.layout.card import BaseCard
from app.ui.components.widgets.button import BaseButton, ToolButton


# TODO: improve jittering when expanding/collapsing with many items

class CollapsibleCategory(BaseCard):
    """Demo version of collapsible category widget."""

    # Signals
    toggled = Signal(bool)
    itemChecked = Signal(str, bool)

    def __init__(self, category_name, parent=None, start_expanded=False):
        super().__init__(parent)

        # Set initial values
        self._category_name = category_name
        self._is_expanded = start_expanded
        self._items = []

        self._setup_header()
        self._setup_content_area()
        self._setup_animation()

        # Set initial state
        if not start_expanded:
            self._content_container.setMaximumHeight(0)

        self._update_expand_state(animate=False)

    def _setup_header(self):
        """Create the category header."""
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

        # Make header clickable
        self._header_widget.mousePressEvent = lambda e: self.toggle()
        self._header_widget.setCursor(Qt.PointingHandCursor)

        self.addWidget(self._header_widget)

    def _setup_content_area(self):
        """Create the collapsible content area."""
        self._content_container = QWidget()
        self._content_container.setObjectName("ContentContainer")

        self._items_layout = QVBoxLayout(self._content_container)
        self._items_layout.setContentsMargins(16, 8, 16, 12)
        self._items_layout.setSpacing(8)

        self.addWidget(self._content_container)

    def _setup_animation(self):
        """Setup animation for expand/collapse."""
        self._animation = QPropertyAnimation(self._content_container, b"maximumHeight")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)

    def _get_content_height(self):
        """Get the natural height of the content."""
        # Get the height hint of the content
        height = self._content_container.sizeHint().height()
        # Add a small buffer to ensure all content is visible
        return height + 20

    def _update_expand_state(self, animate=True):
        """Update visual state based on expansion."""
        if self._is_expanded:
            self._expand_content(animate)
        else:
            self._collapse_content(animate)

        self._update_expand_button()

    def _expand_content(self, animate=True):
        """Expand the content area."""
        if animate:
            # Get the target height
            target_height = self._get_content_height()

            # Setup and start animation
            self._animation.setStartValue(self._content_container.maximumHeight())
            self._animation.setEndValue(target_height)

            # When animation finishes, remove the height restriction
            self._animation.finished.connect(
                lambda: self._content_container.setMaximumHeight(16777215),
                Qt.SingleShotConnection  # Only connect once
            )

            self._animation.start()
        else:
            # Instant expansion
            self._content_container.setMaximumHeight(16777215)

    def _collapse_content(self, animate=True):
        """Collapse the content area."""
        if animate:
            # Get current height
            current_height = self._content_container.height()

            # Setup and start animation
            self._animation.setStartValue(current_height)
            self._animation.setEndValue(0)

            self._animation.start()
        else:
            # Instant collapse
            self._content_container.setMaximumHeight(0)

    def _update_expand_button(self):
        """Update expand button icon."""
        if self._is_expanded:
            icon_name = Icon.ANGLE_DOWN
            self._header_widget.setProperty("is_expanded", "True")
        else:
            icon_name = Icon.ANGLE_RIGHT
            self._header_widget.setProperty("is_expanded", "False")
        BaseButton.setIcon(self._expand_button, icon_name)

        # Force Qt to re-evaluate the stylesheet after property change
        self._header_widget.style().polish(self._header_widget)
        self._expand_button.setStateIconSize(24, 24)

    @property
    def category_name(self):
        return self._category_name

    @property
    def is_expanded(self):
        return self._is_expanded

    def toggle(self):
        """Toggle expansion state."""
        self._is_expanded = not self._is_expanded
        self._update_expand_state(animate=True)
        self.toggled.emit(self._is_expanded)

    def expand(self):
        """Expand the category."""
        if not self._is_expanded:
            self.toggle()

    def collapse(self):
        """Collapse the category."""
        if self._is_expanded:
            self.toggle()

    def addItem(self, item_name):
        """Add a simple checkbox item to the category."""
        checkbox = QCheckBox(item_name)
        checkbox.stateChanged.connect(lambda state: self.itemChecked.emit(item_name, state == Qt.Checked))
        self._items_layout.addWidget(checkbox)
        self._items.append(checkbox)
        return checkbox

    def addShoppingItem(self, shopping_item_widget):
        """Add a ShoppingItem widget to the category."""
        self._items_layout.addWidget(shopping_item_widget)
        self._items.append(shopping_item_widget)

    def setAllItemsChecked(self, checked):
        """Check or uncheck all items in this category."""
        for item in self._items:
            if isinstance(item, QCheckBox):
                item.setChecked(checked)
            elif hasattr(item, 'checkbox'):
                item.checkbox.setChecked(checked)

    def getCheckedItems(self):
        """Return a list of checked item names."""
        checked_items = []
        for item in self._items:
            if isinstance(item, QCheckBox) and item.isChecked():
                checked_items.append(item.text())
            elif hasattr(item, 'checkbox') and item.checkbox.isChecked():
                if hasattr(item, 'item') and hasattr(item.item, 'ingredient_name'):
                    checked_items.append(item.item.ingredient_name)
        return checked_items
