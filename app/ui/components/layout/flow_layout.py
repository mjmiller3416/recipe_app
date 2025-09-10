"""app/ui/components/layout/flow_layout.py

Flow layout component for arranging widgets in a flow-like manner.
Simplified version without animation support.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import List, Optional
from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget, QWidgetItem, QSizePolicy


class FlowLayoutContainer(QWidget):
    """Container widget that holds a FlowLayout."""

    def __init__(self, parent=None, tight: bool = False):
        """
        Initialize FlowLayoutContainer.

        Args:
            parent: Parent widget
            tight: Whether to use tight layout (skip hidden widgets)
        """
        super().__init__(parent)

        # Create the flow layout
        self._flow_layout = FlowLayout(self, tight=tight)

        # Remove margins
        self.setContentsMargins(0, 0, 0, 0)
        self._flow_layout.setContentsMargins(0, 0, 0, 0)

        # Set size policy to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @property
    def layout(self) -> 'FlowLayout':
        """Get the internal flow layout."""
        return self._flow_layout

    def addWidget(self, widget: QWidget):
        """Add a widget to the flow layout."""
        self._flow_layout.addWidget(widget)

    def insertWidget(self, index: int, widget: QWidget):
        """Insert a widget at a specific index."""
        self._flow_layout.insertWidget(index, widget)

    def removeWidget(self, widget: QWidget) -> bool:
        """Remove a widget from the layout."""
        return self._flow_layout.removeWidget(widget)

    def removeAllWidgets(self):
        """Remove all widgets from the layout."""
        self._flow_layout.removeAllWidgets()

    def takeAllWidgets(self):
        """Remove and delete all widgets from the layout."""
        self._flow_layout.takeAllWidgets()

    def count(self) -> int:
        """Return the number of items in the layout."""
        return self._flow_layout.count()

    def setSpacing(self, spacing: int):
        """Set both vertical and horizontal spacing."""
        self._flow_layout.setSpacing(spacing)

    def setVerticalSpacing(self, spacing: int):
        """Set vertical spacing between rows."""
        self._flow_layout.setVerticalSpacing(spacing)

    def setHorizontalSpacing(self, spacing: int):
        """Set horizontal spacing between widgets."""
        self._flow_layout.setHorizontalSpacing(spacing)

    def setTight(self, tight: bool):
        """Set whether to use tight layout."""
        self._flow_layout.setTight(tight)

    def setLayoutMargins(self, left: int, top: int, right: int, bottom: int):
        """Set the content margins for the flow layout."""
        self._flow_layout.setContentsMargins(left, top, right, bottom)

    def removeLayoutMargins(self):
        """Remove all margins from the flow layout."""
        self._flow_layout.setContentsMargins(0, 0, 0, 0)


class FlowLayout(QLayout):
    """Flow layout that arranges widgets horizontally, wrapping to new lines as needed."""

    def __init__(self, parent=None, tight: bool = False):
        """
        Initialize FlowLayout.

        Args:
            parent: Parent widget or layout
            tight: Whether to use tight layout (skip hidden widgets)
        """
        super().__init__(parent)

        self._items: List[QLayoutItem] = []
        self._vertical_spacing = 10
        self._horizontal_spacing = 10
        self._tight = tight

    # ─── Layout Interface ───────────────────────────────────────────────────

    def addItem(self, item: QLayoutItem):
        """Add an item to the layout."""
        self._items.append(item)
        self.invalidate()

    def insertItem(self, index: int, item: QLayoutItem):
        """Insert an item at a specific index."""
        self._items.insert(index, item)
        self.invalidate()

    def addWidget(self, widget: QWidget):
        """Add a widget to the layout."""
        super().addWidget(widget)
        widget.show()
        self.invalidate()

    def insertWidget(self, index: int, widget: QWidget):
        """Insert a widget at a specific index."""
        item = QWidgetItem(widget)
        self.insertItem(index, item)
        self.addChildWidget(widget)
        widget.show()

    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._items)

    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        """Return the item at the given index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int) -> Optional[QLayoutItem]:
        """Remove and return the item at the given index."""
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self.invalidate()
            return item
        return None

    def removeWidget(self, widget: QWidget) -> bool:
        """Remove a widget from the layout."""
        for i, item in enumerate(self._items):
            if item.widget() is widget:
                self.takeAt(i)
                return True
        return False

    def removeAllWidgets(self):
        """Remove all widgets from the layout."""
        while self._items:
            item = self.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)

    def takeAllWidgets(self):
        """Remove and delete all widgets from the layout."""
        while self._items:
            item = self.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    # ─── Layout Geometry ────────────────────────────────────────────────────

    def setGeometry(self, rect: QRect):
        """Set the geometry of the layout."""
        super().setGeometry(rect)
        self._do_layout(rect)

    def sizeHint(self) -> QSize:
        """Return the preferred size of the layout."""
        width = 800  # Default preferred width
        height = self.heightForWidth(width)
        return QSize(width, height)

    def minimumSize(self) -> QSize:
        """Return the minimum size of the layout."""
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom()
        )
        return size

    def expandingDirections(self) -> Qt.Orientations:
        """Return the expanding directions of the layout."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        """Return whether the layout has height-for-width."""
        return True

    def heightForWidth(self, width: int) -> int:
        """Calculate the height needed for the given width."""
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    # ─── Spacing Configuration ──────────────────────────────────────────────

    def setVerticalSpacing(self, spacing: int):
        """Set vertical spacing between rows."""
        self._vertical_spacing = spacing
        self.invalidate()

    def verticalSpacing(self) -> int:
        """Get vertical spacing between rows."""
        return self._vertical_spacing

    def setHorizontalSpacing(self, spacing: int):
        """Set horizontal spacing between widgets."""
        self._horizontal_spacing = spacing
        self.invalidate()

    def horizontalSpacing(self) -> int:
        """Get horizontal spacing between widgets."""
        return self._horizontal_spacing

    def setSpacing(self, spacing: int):
        """Set both vertical and horizontal spacing."""
        self.setVerticalSpacing(spacing)
        self.setHorizontalSpacing(spacing)

    # ─── Layout Configuration ───────────────────────────────────────────────

    def setTight(self, tight: bool):
        """Set whether to use tight layout (skip hidden widgets)."""
        self._tight = tight
        self.invalidate()

    def isTight(self) -> bool:
        """Return whether tight layout is enabled."""
        return self._tight

    # ─── Private Methods ────────────────────────────────────────────────────

    def _do_layout(self, rect: QRect, test_only: bool = False) -> int:
        """
        Perform the actual layout calculation and optionally apply it.

        Args:
            rect: The rectangle to layout within
            test_only: If True, only calculate height without applying positions

        Returns:
            The total height needed for the layout
        """
        if not self._items:
            return rect.height() if rect.height() > 0 else 100

        margins = self.contentsMargins()
        effective_rect = rect.adjusted(
            margins.left(), margins.top(),
            -margins.right(), -margins.bottom()
        )

        # Ensure we have a valid width to work with
        if effective_rect.width() <= 0:
            return rect.height() if rect.height() > 0 else 100

        x = effective_rect.x()
        y = effective_rect.y()
        row_height = 0
        max_width = effective_rect.width()

        for item in self._items:
            widget = item.widget()

            # Skip hidden widgets if tight layout is enabled
            if widget and not widget.isVisible() and self._tight:
                continue

            item_size = item.sizeHint()

            # Ensure valid size
            if not item_size.isValid():
                item_size = QSize(200, 250)  # Default size for invalid items

            # Check if we need to wrap to next row
            if x + item_size.width() > effective_rect.x() + max_width and row_height > 0:
                x = effective_rect.x()
                y += row_height + self._vertical_spacing
                row_height = 0

            # Apply position if not testing
            if not test_only and widget:
                widget.setGeometry(QRect(QPoint(x, y), item_size))

            # Update position for next widget
            x += item_size.width() + self._horizontal_spacing
            row_height = max(row_height, item_size.height())

        # Calculate total height
        total_height = y + row_height + margins.bottom() - rect.y()

        # Update parent widget's minimum height if we have one and not testing
        if not test_only and self.parentWidget():
            self.parentWidget().setMinimumHeight(total_height)

        return total_height

    def invalidate(self):
        """Invalidate the layout and trigger a relayout."""
        super().invalidate()
        self.update()

        # Also update parent widget if it exists
        if self.parentWidget():
            self.parentWidget().updateGeometry()


# ─── Convenience Factory Function ───────────────────────────────────────────
def create_flow_container(parent=None, tight: bool = False) -> FlowLayoutContainer:
    """
    Create a flow layout container widget.

    Args:
        parent: Parent widget
        tight: Whether to use tight layout (skip hidden widgets)

    Returns:
        FlowLayoutContainer: A widget containing a flow layout
    """
    return FlowLayoutContainer(parent, tight=tight)
