"""app/ui/components/navigation/nav_button.py

A composite navigation button that synchronizes its hover and checked state with its child icon and label.
Integrated with the new icon system for dynamic theming.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from app.ui.components.widgets import ToolButton
from app.theme_manager.icon.config import Name, Type


# ── Class Definition ────────────────────────────────────────────────────────────
class NavButton(QPushButton):
    """
    A composite navigation button that synchronizes its hover and checked
    state with its child icon and label.
    """
    def __init__(
        self,
        text: str,
        name: Name,
        height: int = 40,
        width: int | None = None,
        spacing: int = 10,
        checkable: bool = True,
        parent=None
    ):
        super().__init__("", parent)

        self.setCheckable(checkable)

        # ── Internal Widgets ──
        self._icon = ToolButton(
            icon=icon_name,
            checkable=checkable,
        )
        self._icon.setStyleSheet("border: none; background-color: transparent;")
        self._icon.setFocusPolicy(Qt.NoFocus)
        self._icon.setAttribute(Qt.WA_TransparentForMouseEvents)

        self._label = QLabel(text)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # link state changes to update visuals
        self.toggled.connect(self._update_visuals)
        self._update_visuals()

        # ─── Layout & Sizing ───────────
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(40, 0, 10, 0)
        self._layout.setSpacing(spacing)
        self._layout.addWidget(self._icon)
        self._layout.addWidget(self._label)
        self._layout.addStretch()
        self.setFixedHeight(height)
        if width is not None:
            self.setFixedWidth(width)

    def _update_visuals(self) -> None:
        """Helper to synchronize the internal icon state and set label style property."""
        # Sync the internal ToolButton's checked state with our state
        self._icon.setChecked(self.isChecked())

        # Set appropriate label state for styling
        if self.isChecked():
            self._label.setProperty("state", "CHECKED")
        elif self.underMouse():
            self._label.setProperty("state", "HOVER")
        else:
            self._label.setProperty("state", "DEFAULT")

        self.style().unpolish(self._label)
        self.style().polish(self._label)

    # ─── Public Methods & Overrides ──────────────────────────────────────────
    def setChecked(self, checked: bool) -> None:
        """Override setChecked to force a style update."""
        super().setChecked(checked)
        # Force Qt to re-evaluate the stylesheet for this widget and its children
        self.style().unpolish(self)
        self.style().polish(self)

    def enterEvent(self, event):
        """Override enterEvent to update icon and force style update."""
        super().enterEvent(event)
        self._update_visuals()
        # Re-apply styles to update child widgets like the QLabel
        self.style().polish(self)

    def leaveEvent(self, event):
        """Override leaveEvent to update icon and force style update."""
        super().leaveEvent(event)
        self._update_visuals()
        # Re-apply styles to update child widgets like the QLabel
        self.style().polish(self)

    def setText(self, text: str) -> None:
        """Sets the text of the internal label."""
        self._label.setText(text)

    def text(self) -> str:
        """Returns the text of the internal label."""
        return self._label.text()
