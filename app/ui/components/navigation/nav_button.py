"""app/ui/components/navigation/nav_button.py

A composite navigation button that synchronizes its hover and checked state with its child icon and label.
Integrated with the new icon system for dynamic theming.

⚠️ Class is has been moved to app/ui/components/widgets/button.py
and will be removed from this location in future releases ⚠️
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from app.style import Theme
from app.style.theme.config import Qss
from app.style.icon.config import Name, Type
from app.ui.components.widgets import ToolButton


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
        self.setObjectName("NavButton")

        self.setCheckable(checkable)

        # Register for component-specific styling
        Theme.register_widget(self, Qss.NAV_BUTTON)

        # ── Internal Widgets ──
        self._icon = ToolButton(Type.SECONDARY)
        self._icon.setIcon(name)
        self._icon.setButtonCheckable(checkable)
        self._icon.setFocusPolicy(Qt.NoFocus)

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
        # sync the internal ToolButton's checked state with our state
        self._icon.setChecked(self.isChecked())

        # set appropriate label state for styling
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

        self.style().unpolish(self)
        self.style().polish(self)

    def enterEvent(self, event):
        """Override enterEvent to update icon and force style update."""
        super().enterEvent(event)
        self._update_visuals()

        # Manually trigger icon hover state
        self._icon.enterEvent(event)

        self.style().polish(self)

    def leaveEvent(self, event):
        """Override leaveEvent to update icon and force style update."""
        super().leaveEvent(event)
        self._update_visuals()

        # Manually trigger icon leave state
        self._icon.leaveEvent(event)

        self.style().polish(self)

    def setText(self, text: str) -> None:
        """Sets the text of the internal label."""
        self._label.setText(text)

    def text(self) -> str:
        """Returns the text of the internal label."""
        return self._label.text()
