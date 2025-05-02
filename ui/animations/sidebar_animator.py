# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Property, QObject


# ── Class Definition ────────────────────────────────────────────────────────────
class SidebarAnimator(QObject):
    """ SidebarAnimator is a QObject that manages the width of a sidebar widget. """
    def __init__(self, sidebar):
        super().__init__()
        self._value = sidebar.width()
        self.sidebar = sidebar

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = max(0, value)  # Clamp to non-negative
        self.sidebar.setMaximumWidth(self._value)

    value = Property(int, getValue, setValue)