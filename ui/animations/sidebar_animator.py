# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Property, QObject
from PySide6.QtWidgets import QWidget


# ── Class Definition ────────────────────────────────────────────────────────────
class SidebarAnimator(QObject):
    """A QObject wrapper that exposes a 'value' property for animating the sidebar's width.

    This is used with QPropertyAnimation to smoothly expand or collapse the sidebar
    by adjusting its maximum width.
    """
    def __init__(self, sidebar: QWidget):
        """ Initializes the SidebarAnimator with a reference to the sidebar widget.

        Args:
            sidebar (Sidebar): The sidebar widget to animate.
        """
        super().__init__()
        self._value = sidebar.width()
        self.sidebar = sidebar

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = max(0, value)  # Clamp to non-negative
        print(f"Setting max width to {self._value}")
        self.sidebar.setMaximumWidth(self._value)
        print(f"→ Actual width is now: {self.sidebar.width()}")
    value = Property(int, getValue, setValue)