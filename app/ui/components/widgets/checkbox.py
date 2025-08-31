"""app/ui/components/widgets/checkbox.py

Basic checkbox widget for use in dropdown menus and forms.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox


# ── CheckBox ────────────────────────────────────────────────────────────────────────────────────────────────
class CheckBox(QCheckBox):
    """Custom checkbox widget with enhanced styling support."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("CheckBox")
