"""app/ui/components/layout/flow_layout.py

Provides the FlowLayout class for arranging widgets in a wrapping row layout.
"""

# ── Imports ────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout


# ── Class Definition ───────────────────────────────────────────────────────────
class FlowLayout(QLayout):
    """A responsive flow layout that centers widgets and wraps as needed."""

    def __init__(self, parent=None, margin: int = 0, spacing: int = 45) -> None:
        """Initialize the layout with optional margins and spacing."""
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing

    def addItem(self, item) -> None:
        """Add a layout item."""
        self._items.append(item)

    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._items)

    def itemAt(self, index: int):
        """Return the layout item at *index* or ``None`` if out of range."""
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index: int):
        """Remove and return the layout item at *index*."""
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect: QRect, test_only: bool) -> int:
        TOP_PADDING = 20
        y = rect.y() + TOP_PADDING
        row = []
        row_width = 0
        row_height = 0

        def layout_row(items, y_pos):
            total_width = sum(i.sizeHint().width() for i in items) + self._spacing * (len(items) - 1)
            offset = (rect.width() - total_width) // 2
            x = rect.x() + offset
            for item in items:
                size = item.sizeHint()
                if not test_only:
                    item.setGeometry(QRect(QPoint(x, y_pos), size))
                x += size.width() + self._spacing
            return y_pos + row_height + self._spacing

        for item in self._items:
            size = item.sizeHint()
            if row and (row_width + size.width() + self._spacing > rect.width()):
                y = layout_row(row, y)
                row = []
                row_width = 0
                row_height = 0
            row.append(item)
            row_width += size.width() + (self._spacing if row else 0)
            row_height = max(row_height, size.height())

        if row:
            y = layout_row(row, y)

        return y - rect.y()
